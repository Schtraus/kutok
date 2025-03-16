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




document.addEventListener('DOMContentLoaded', () => {
    const threadId = document.getElementById('thread-id').textContent.trim(); // Просто получаем текст
    const commentSocket = new WebSocket(
        `wss://${window.location.host}/ws/thread/${threadId}/`
    );

    commentSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);

        // Если текущая страница не первая, перенаправляем на первую страницу
        const currentPage = new URLSearchParams(window.location.search).get('page');
        if (currentPage && currentPage !== '1') {
            window.location.href = window.location.pathname;  // Перенаправляем на первую страницу
            return;
        }

        // Получаем контейнер для комментариев
        const commentContainer = document.getElementById('comments-container');

        // Формируем новый комментарий
        const newComment = `
            <li class="list-group-item mb-3 p-3 shadow-sm rounded fade-in blinking" id="comment-${data.id}">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <strong>${data.author}</strong>
                        <span class="text-muted small">— ${new Date(data.created_at).toLocaleString('en-GB', {
                                day: '2-digit',
                                month: 'short',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                            })}
                        </span>
                    </div>
                    <div class="ms-auto">
                        ${data.current_user_authenticated && data.current_user_is_author ? `
                            <!-- Редактировать комментарий -->
                            <a href="#" class="btn btn-warning btn-sm edit-comment" data-id="${data.id}">
                                <i class="bi bi-pencil"></i>
                            </a>
                            <!-- Удалить комментарий -->
                            <a href="#" class="btn btn-danger btn-sm delete-comment" data-id="${data.id}">
                                <i class="bi bi-trash"></i>
                            </a>
                        ` : ''}
                        ${data.current_user_authenticated && !data.current_user_is_author ? `
                            <!-- Пожаловаться на комментарий -->
                            <a href="#" class="btn btn-danger btn-sm report-comment" data-id="${data.id}">
                                <i class="bi bi-flag"></i>
                            </a>
                        ` : ''}
                    </div>
                </div>
                <p class="comment-content mb-0 mt-2">${data.content.replace(/\n/g, '<br>')}</p>
            </li>
        `;


        // Добавляем новый комментарий в начало списка
        commentContainer.insertAdjacentHTML('afterbegin', newComment);

        // Убираем анимацию через 3 секунды
        const newCommentElement = document.getElementById(`comment-${data.id}`);
        setTimeout(() => {
            console.log("Убираем анимацию с комментария:", data.id); // Отладочное сообщение
            newCommentElement.classList.remove('blinking');
        }, 3000); // 3 секунды

        let notificationSound;
        if (data.current_user_is_author) {
            // Звук для автора комментария
            notificationSound = new Audio('/static/sounds/sent_comment.mp3');
        } else {
            // Звук для остальных пользователей
            notificationSound = new Audio('/static/sounds/received_comment.wav');
        }
        notificationSound.play();

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
            // Если нажат Shift + Enter, добавляем перенос строки
            if (event.shiftKey) {
                return; // Не отправляем комментарий, разрешаем перенос строки
            }

            // Если нажат только Enter, отправляем комментарий
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


document.addEventListener('DOMContentLoaded', () => {
    const threadSlug = document.getElementById('thread-slug').textContent.trim(); // Получаем slug треда
    const commentsContainer = document.getElementById('comments-container');
    const loadMoreButton = document.getElementById('load-more-comments');
    let offset = 25; // Начальное значение offset (уже загружено 25 комментариев)

    // Функция для загрузки комментариев
    async function loadComments() {
        const response = await fetch(`/load-more-comments/${threadSlug}/?offset=${offset}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        });
        const data = await response.json();

        if (data.comments_html) {
            // Добавляем новые комментарии в контейнер
            commentsContainer.insertAdjacentHTML('beforeend', data.comments_html);
            offset += 25; // Увеличиваем offset

            // Скрываем кнопку, если больше нет комментариев
            if (!data.has_more) {
                loadMoreButton.style.display = 'none';
            }
        } else {
            loadMoreButton.style.display = 'none'; // Скрываем кнопку, если комментариев нет
        }
    }

    // Обработчик для кнопки "Посмотреть еще"
    loadMoreButton.addEventListener('click', loadComments);
});