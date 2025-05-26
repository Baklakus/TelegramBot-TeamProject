document.addEventListener('DOMContentLoaded', function() {
    const surveysContainer = document.getElementById('surveys-container');
    
    // Загружаем опросы из localStorage
    const surveys = JSON.parse(localStorage.getItem('surveys')) || [];
    
    if (surveys.length === 0) {
        surveysContainer.innerHTML = '<p>Нет опросов</p>';
        return;
    }
    
    // Отображаем каждый опрос
    surveys.forEach((survey, index) => {
        const surveyElement = document.createElement('div');
        surveyElement.className = 'survey';
        surveyElement.innerHTML = `
            <h3>${survey.title}</h3>
            <p>Создан: ${new Date(survey.createdAt).toLocaleString()}</p>
            <p>Вопросов: ${survey.questions.length}</p>
            <button onclick="location.href='survey.html?id=${index}'">Пройти опрос</button>
        `;
        surveysContainer.appendChild(surveyElement);
    });
});