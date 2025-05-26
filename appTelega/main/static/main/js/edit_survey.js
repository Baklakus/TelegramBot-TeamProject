document.addEventListener('DOMContentLoaded', function () {
    const questionsContainer = document.getElementById('questions-container');
    const addQuestionBtn = document.getElementById('add-question');
    const form = document.getElementById('surveyForm');
    const updateBtn = document.getElementById('update-survey');
    const postUrl = form.dataset.url;
    const indexUrl = form.dataset.indexUrl;

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

    // Удаление опроса через форму
    const deleteSurveyBtn = document.getElementById('delete-survey-btn');
    if (deleteSurveyBtn) {
        deleteSurveyBtn.addEventListener('click', async function () {
            const surveyId = form.dataset.surveyId; // получаем ID опроса из атрибута data-свойства формы

            if (confirm('Вы уверены, что хотите удалить этот опрос?')) {
                try {
                    const response = await fetch(`/survey/${surveyId}/delete/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken'),
                        }
                    });

                    if (response.ok) {
                        alert('Опрос успешно удален!');
                        window.location.href = indexUrl;  // Перенаправляем на страницу с опросами
                    } else {
                        throw new Error('Ошибка при удалении опроса');
                    }
                } catch (error) {
                    alert(error.message);
                }
            }
        });
    }

    // Логика добавления нового вопроса и варианта
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
                    <button type="button" class="delete-option">Удалить</button>
                </div>
                <div class="option-block">
                    <input type="text" placeholder="Вариант ответа" required>
                    <button type="button" class="delete-option">Удалить</button>
                </div>
            </div>
            <button type="button" class="add-option">+ Добавить вариант</button>
        `;
        questionsContainer.appendChild(questionBlock);
    }

    function addNewOption(optionsContainer) {
        const optionBlock = document.createElement('div');
        optionBlock.className = 'option-block';
        optionBlock.innerHTML = `
            <input type="text" placeholder="Вариант ответа" required>
            <button type="button" class="delete-option">Удалить</button>
        `;
        optionsContainer.appendChild(optionBlock);
    }

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

    addQuestionBtn.addEventListener('click', addNewQuestion);

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const errors = [];
        const surveyTitle = document.getElementById('survey-title').value.trim();
        const surveyDescription = document.getElementById('survey-description').value.trim();
        const questionBlocks = document.querySelectorAll('.question-block');

        if (!surveyTitle) errors.push('Введите название опроса');
        if (questionBlocks.length === 0) errors.push('Добавьте хотя бы один вопрос');

        const questions = [];

        questionBlocks.forEach((block, index) => {
            const questionText = block.querySelector('.question-input').value.trim();
            const required = block.querySelector('.question-required')?.checked ?? false;
            const options = Array.from(block.querySelectorAll('.option-block')).map(optBlock => {
                return {
                    text: optBlock.querySelector('input').value.trim()
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
                required: true,
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
            window.location.href = indexUrl;

        } catch (error) {
            alert(`Ошибка: ${error.message}`);
        }
    });
});
