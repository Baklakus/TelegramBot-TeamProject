document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('surveyForm');
    const postUrl = form.dataset.url;  // URL для отправки данных формы
    const indexUrl = form.dataset.indexUrl;  // URL для перенаправления на главную страницу
    const surveyId = form.dataset.surveyId;  // Получаем ID опроса из атрибута формы

    if (!surveyId) {
        console.error("Survey ID не найден!");
        return;
    }

    // Функция для получения CSRF токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Добавление нового варианта
    function addNewOption(optionsContainer) {
        const optionBlock = document.createElement('div');
        optionBlock.className = 'option-block';
        optionBlock.innerHTML = `
            <input type="text" placeholder="Вариант ответа" required>
            <label for="correct-option">Правильный?</label>
            <input type="checkbox" class="correct-option">
            <button type="button" class="delete-option">Удалить</button>
        `;
        optionsContainer.appendChild(optionBlock);
    }

    // Добавление нового вопроса
    function addNewQuestion() {
        const questionBlock = document.createElement('div');
        questionBlock.className = 'question-block';
        questionBlock.innerHTML = `
            <div>
                <label>Вопрос:</label>
                <input type="text" class="question-input" required>
            </div>
            <div>
                <label>Обязательный?</label>
                <input type="checkbox" class="question-required">
            </div>
            <div class="options-container">
                <div class="option-block">
                    <input type="text" placeholder="Вариант ответа" required>
                    <label for="correct-option">Правильный?</label>
                    <input type="checkbox" class="correct-option">
                    <button type="button" class="delete-option">Удалить</button>
                </div>
                <div class="option-block">
                    <input type="text" placeholder="Вариант ответа" required>
                    <label for="correct-option">Правильный?</label>
                    <input type="checkbox" class="correct-option">
                    <button type="button" class="delete-option">Удалить</button>
                </div>
            </div>
            <button type="button" class="add-option">+ Добавить вариант</button>
        `;
        questionsContainer.appendChild(questionBlock);
    }

    // Обработчик для добавления нового варианта ответа
    const questionsContainer = document.getElementById('questions-container');
    questionsContainer.addEventListener('click', function (e) {
        if (e.target.classList.contains('delete-option')) {
            const optionBlock = e.target.closest('.option-block');
            const optionsContainer = optionBlock.parentElement;
            if (optionsContainer.querySelectorAll('.option-block').length > 2) {
                optionBlock.remove();
            } else {
                alert('Должно быть минимум 2 варианта ответа!');
            }
        }

        if (e.target.classList.contains('add-option')) {
            const questionBlock = e.target.closest('.question-block');
            const optionsContainer = questionBlock.querySelector('.options-container');
            addNewOption(optionsContainer);
        }

        // Обработчик для удаления вопроса
        if (e.target.classList.contains('delete-question')) {
            const questionBlock = e.target.closest('.question-block');
            const questionId = questionBlock.getAttribute('data-question-id');
            const confirmDelete = confirm('Вы уверены, что хотите удалить этот вопрос?');

            if (confirmDelete) {
                // Отправляем запрос на сервер для удаления вопроса
                fetch(`/survey/${surveyId}/delete_question/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question_id: questionId })
                })
                .then(response => {
                    if (response.ok) {
                        questionBlock.remove();
                    } else {
                        alert('Ошибка при удалении вопроса');
                    }
                })
                .catch(error => {
                    alert('Ошибка при удалении вопроса');
                });
            }
        }
    });

    // Обработчик для добавления нового вопроса
    const addQuestionBtn = document.getElementById('add-question');
    if (addQuestionBtn) {
        addQuestionBtn.addEventListener('click', addNewQuestion);
    }

    // Обработчик отправки формы
    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const errors = [];
        const surveyTitle = document.getElementById('survey-title').value.trim();
        const surveyDescription = document.getElementById('survey-description').value.trim();
        const questionBlocks = document.querySelectorAll('.question-block');

        if (!surveyTitle) errors.push('Введите название опроса');
        if (questionBlocks.length === 0) errors.push('Добавьте хотя бы один вопрос');

        const questions = [];

        // Проверка всех вопросов и вариантов
        questionBlocks.forEach((block, index) => {
            const questionText = block.querySelector('.question-input').value.trim();
            const required = block.querySelector('.question-required').checked;
            const options = Array.from(block.querySelectorAll('.option-block')).map(optBlock => {
                return {
                    text: optBlock.querySelector('input').value.trim(),
                    is_correct: optBlock.querySelector('.correct-option').checked  // Считываем состояние галочки "Правильный?"
                };
            });

            if (!questionText) errors.push(`Вопрос ${index + 1}: не заполнен`);
            if (options.some(opt => !opt.text)) errors.push(`Вопрос ${index + 1}: есть пустые варианты`);
            if (new Set(options.map(o => o.text)).size !== options.length) {
                errors.push(`Вопрос ${index + 1}: повторяющиеся варианты`);
            }

            questions.push({
                text: questionText,
                type: 'single_choice',  // Тип вопроса
                required: required,
                options: options
            });
        });

        if (errors.length > 0) {
            alert(errors.join('\n'));
            return;
        }

        const formData = {
            title: surveyTitle,
            description: surveyDescription,
            questions: questions
        };

        try {
            const response = await fetch(postUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Ошибка сервера');
            }

            alert('Опрос успешно обновлён!');
            window.location.href = indexUrl;  // Перенаправление на главную страницу

        } catch (error) {
            alert(`Ошибка: ${error.message}`);
        }
    });
});
