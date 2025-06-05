document.addEventListener('DOMContentLoaded', function () {
    const questionsContainer = document.getElementById('questions-container');
    const addQuestionBtn = document.getElementById('add-question');
    const form = document.getElementById('surveyForm');
    const postUrl = form.dataset.url; // URL для отправки данных формы

    // Функция для получения CSRF токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Функция для добавления нового вопроса
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

    // Функция для добавления нового варианта
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

    // Обработчик удаления варианта ответа
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
    });

    // Обработчик добавления нового вопроса
    addQuestionBtn.addEventListener('click', addNewQuestion);

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
                    is_correct: optBlock.querySelector('.correct-option').checked
                };
            });

            if (!questionText) errors.push(`Вопрос ${index + 1}: не заполнен`);
            if (options.some(opt => !opt.text)) errors.push(`Вопрос ${index + 1}: есть пустые варианты`);
            if (new Set(options.map(o => o.text)).size !== options.length) {
                errors.push(`Вопрос ${index + 1}: повторяющиеся варианты`);
            }

            questions.push({
                text: questionText,
                type: 'single_choice',
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

            alert('Опрос успешно создан!');
            window.location.href = window.surveyUrls.index; // Перенаправление на главную страницу

        } catch (error) {
            alert(`Ошибка: ${error.message}`);
        }
    });
});
