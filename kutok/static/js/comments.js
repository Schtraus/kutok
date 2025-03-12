// // Открытие модального окна и заполнение формы
// document.querySelectorAll('.edit-comment').forEach(button => {
//     button.addEventListener('click', function (e) {
//         e.preventDefault();

//         // Получаем текущий комментарий
//         var commentItem = button.closest('li');
//         var commentId = commentItem.id.replace('comment-', '');
//         var commentContent = commentItem.querySelector('.comment-content').innerHTML.trim();

//         // Преобразуем HTML переносы в текстовые переносы строк и декодируем HTML-сущности
//         commentContent = commentContent.replace(/<br\s*\/?>/g, '\n');
//         commentContent = decodeEntities(commentContent);

//         // Заполняем форму в модальном окне
//         document.getElementById('commentContent').value = commentContent;
//         document.getElementById('commentId').value = commentId;

//         // Открываем модальное окно
//         var editCommentModal = new bootstrap.Modal(document.getElementById('editCommentModal'));
//         editCommentModal.show();
//     });
// });

function decodeEntities(str) {
    var textarea = document.createElement('textarea');
    textarea.innerHTML = str;
    return textarea.value;
}

// Обработка отправки формы редактирования
document.getElementById('editCommentForm').addEventListener('submit', function (e) {
    e.preventDefault();

    var commentId = document.getElementById('commentId').value;
    var updatedContent = document.getElementById('commentContent').value;

    // Здесь необходимо отправить запрос на сервер для обновления комментария
    fetch('/comments/update/' + commentId + '/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value

        },
        body: JSON.stringify({
            content: updatedContent
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.querySelector('#comment-' + commentId + ' .comment-content').innerHTML = updatedContent.replace(/\n/g, '<br>');
            var editCommentModal = bootstrap.Modal.getInstance(document.getElementById('editCommentModal'));
            editCommentModal.hide();
        } else {
            alert('Ошибка при обновлении комментария.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Произошла ошибка.');
    });
});

// // Открытие модального окна для жалобы
// document.querySelectorAll('.report-comment').forEach(button => {
//     button.addEventListener('click', function (e) {
//         e.preventDefault();
//         const commentId = button.getAttribute('data-id');
//         document.getElementById('reportCommentId').value = commentId;

//         const reportModal = new bootstrap.Modal(document.getElementById('reportCommentModal'));
//         reportModal.show();
//     });
// });

// Обработка отправки формы жалобы
document.getElementById('reportCommentForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const commentId = document.getElementById('reportCommentId').value;
    const reason = document.getElementById('reportReason').value;

    console.log(`/comments/report/${commentId}/`);  // Логируем URL
    console.log({
        reason: reason
    });

    fetch(`/comments/report/${commentId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            reason: reason
        })
    })
    .then(response => response.json())  // Парсим ответ как JSON
    .then(data => {
        console.log('Response Data:', data); // Теперь данные уже объект
        if (data.success) {
            alert('Жалоба отправлена');
            const reportModal = bootstrap.Modal.getInstance(document.getElementById('reportCommentModal'));
            reportModal.hide();
        } else {
            alert(data.error);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка');
    });
});


// document.querySelectorAll('.delete-comment').forEach(button => {
//     button.addEventListener('click', function (e) {
//         e.preventDefault();

//         const commentId = button.getAttribute('data-id');
//         if (confirm('Вы уверены, что хотите удалить этот комментарий?')) {
//             // Отправка запроса на сервер для удаления комментария
//             fetch(`/comments/delete/${commentId}/`, {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json',
//                     'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
//                 }
//             })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.success) {
//                     // Успешное удаление - удаляем комментарий из DOM
//                     const commentItem = document.getElementById('comment-' + commentId);
//                     if (commentItem) {
//                         commentItem.remove();
//                     }
//                     alert('Комментарий удален');
//                 } else {
//                     alert('Ошибка при удалении комментария');
//                 }
//             })
//             .catch(error => {
//                 console.error('Ошибка:', error);
//                 alert('Произошла ошибка при удалении комментария');
//             });
//         }
//     });
// });


document.addEventListener('DOMContentLoaded', () => {
    console.log("JavaScript загружен!");
    const threadSlug = document.getElementById('thread-slug').textContent.trim(); // Просто получаем текст
    const commentSocket = new WebSocket(
        `wss://${window.location.host}/ws/thread/${threadSlug}/`
    );
    console.log(window.location.host)
    commentSocket.onopen = function() {
        console.log("WebSocket connection established");
    };

    commentSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        // console.log("Received comment data:", data); // Для отладки
        console.log("User data:", data.user); // Проверить доступность данных пользователя

        // Получаем контейнер для комментариев
        const commentContainer = document.getElementById('comments-container');

       // Проверяем, что текущий пользователь авторизован
        const isUserAuthenticated = data.is_authenticated;

        // Логика отображения кнопок для редактирования и удаления
        const isCurrentUserAuthor = data.is_author;  // Проверяем, является ли текущий пользователь автором комментария

            // Для отладки
        console.log(`is_current_user_author: ${isCurrentUserAuthor}`);
        console.log(data.is_author);  // Проверка, правильно ли вычисляется автор
        console.log(data.is_authenticated);  // Проверка, авторизован ли пользователь



        // Проверяем, есть ли данные о пользователе
        if (data.user) {
            console.log("User is authenticated:", data.user.is_authenticated);
        }

        // Формируем новый комментарий
        const newComment = `
            <li class="list-group-item" id="comment-${data.id}">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${data.author}</strong>
                        <span class="text-muted small">— ${data.created_at}</span>
                    </div>
                    <div class="ms-auto">
                        ${data.is_authenticated ? `
                            ${data.is_author ? `
                                <!-- Редактировать комментарий -->
                                <a href="#" class="btn btn-warning btn-sm edit-comment" data-id="${data.id}">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="black" viewBox="0 0 16 16">
                                        <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"></path>
                                        <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5z"/>
                                    </svg>
                                </a>
                                <!-- Удалить комментарий -->
                                <a href="#" class="btn btn-danger btn-sm delete-comment" data-id="${data.id}">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" viewBox="0 0 15 15">
                                        <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                                        <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                                    </svg>
                                </a>
                            ` : `
                                <!-- Пожаловаться на комментарий -->
                                <a href="#" class="btn btn-danger btn-sm report-comment" data-id="${data.id}">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" viewBox="0 0 16 16">
                                        <path d="M14.778.085A.5.5 0 0 1 15 .5V8a.5.5 0 0 1-.314.464L14.5 8l.186.464-.003.001-.006.003-.023.009a12 12 0 0 1-.397.15c-.264.095-.631.223-1.047.35-.816.252-1.879.523-2.71.523-.847 0-1.548-.28-2.158-.525l-.028-.01C7.68 8.71 7.14 8.5 6.5 8.5c-.7 0-1.638.23-2.437.477A20 20 0 0 0 3 9.342V15.5a.5.5 0 0 1-1 0V.5a.5.5 0 0 1 1 0v.282c.226-.079.496-.17.79-.26C4.606.272 5.67 0 6.5 0c.84 0 1.524.277 2.121.519l.043.018C9.286.788 9.828 1 10.5 1c.7 0 1.638-.23 2.437-.477a20 20 0 0 0 1.349-.476l.019-.007.004-.002h.001M14 1.221c-.22.078-.48.167-.766.255-.81.252-1.872.523-2.734.523-.886 0-1.592-.286-2.203-.534l-.008-.003C7.662 1.21 7.139 1 6.5 1c-.669 0-1.606.229-2.415.478A21 21 0 0 0 3 1.845v6.433c.22-.078.48-.167.766-.255C4.576 7.77 5.638 7.5 6.5 7.5c.847 0 1.548.28 2.158.525l.028.01C9.32 8.29 9.86 8.5 10.5 8.5c.668 0 1.606-.229 2.415-.478A21 21 0 0 0 14 7.655V1.222z"/>
                                    </svg>
                                </a>
                            `}
                        ` : ''}
                    </div>
                </div>

                <p class="comment-content mb-0">${data.content}</p>
            </li>
        `;





        // Добавляем новый комментарий в начало списка
        commentContainer.insertAdjacentHTML('afterbegin', newComment);

        // Обновление счетчика комментариев
        const commentCount = document.getElementById('commentCount');
        if (commentCount) {
            commentCount.textContent = `Коментарі (${data.comment_count})`; // Обновление текста счетчика
        }
    };

    const commentForm = document.getElementById('commentForm');
    const submitButton = document.getElementById('submitCommentBtn');
    const commentInput = document.getElementById('commentInput');

    // Отправка комментария через WebSocket при нажатии на кнопку
    submitButton.addEventListener('click', function() {
        const comment = commentInput.value;

        if (comment.trim()) {
            console.log("Sending comment via WebSocket");
            commentSocket.send(JSON.stringify({
                'content': comment
            }));
            commentInput.value = ''; // Очистить поле ввода
        }
    });

    // Отправка комментария через WebSocket при нажатии Enter
    commentInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();  // Отменить действие по умолчанию (отправку формы)
            const comment = commentInput.value;

            if (comment.trim()) {
                console.log("Sending comment via WebSocket");
                commentSocket.send(JSON.stringify({
                    'content': comment
                }));
                commentInput.value = ''; // Очистить поле ввода
            }
        }
    });
});


// Делегирование событий на контейнер комментариев
document.getElementById('comments-container').addEventListener('click', function(e) {
    if (e.target.closest('.edit-comment')) {
        e.preventDefault();
        const button = e.target.closest('.edit-comment');
        const commentItem = button.closest('li');
        const commentId = commentItem.id.replace('comment-', '');
        const commentContent = commentItem.querySelector('.comment-content').innerHTML.trim();

        const decodedContent = decodeEntities(commentContent.replace(/<br\s*\/?>/g, '\n'));

        document.getElementById('commentContent').value = decodedContent;
        document.getElementById('commentId').value = commentId;

        const editCommentModal = new bootstrap.Modal(document.getElementById('editCommentModal'));
        editCommentModal.show();
    }

    if (e.target.closest('.delete-comment')) {
        e.preventDefault();
        const button = e.target.closest('.delete-comment');
        const commentId = button.getAttribute('data-id');
        console.log('Клик по кнопке удаления', e.target);

        if (confirm('Вы уверены, что хотите удалить этот комментарий?')) {
            fetch(`/comments/delete/${commentId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const commentItem = document.getElementById('comment-' + commentId);
                    if (commentItem) {
                        commentItem.remove();
                    }
                    alert('Комментарий удален');
                } else {
                    alert('Ошибка при удалении комментария');
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при удалении комментария');
            });
        }
    }

    if (e.target.closest('.report-comment')) {
        e.preventDefault();
        const button = e.target.closest('.report-comment');
        const commentId = button.getAttribute('data-id');

        document.getElementById('reportCommentId').value = commentId;
        const reportModal = new bootstrap.Modal(document.getElementById('reportCommentModal'));
        reportModal.show();
    }
});

function decodeEntities(str) {
    const textarea = document.createElement('textarea');
    textarea.innerHTML = str;
    return textarea.value;
}