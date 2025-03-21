function formatLocalTime(utcTimeString) {
    const date = new Date(utcTimeString);
    return date.toLocaleString('ru-RU', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
    }).replace(/\./g, '/'); // Заменяем точки на слэши
}

// Применяем функцию ко всем элементам с классом .comment-date
document.querySelectorAll('.comment-date').forEach(element => {
    const utcTimeString = element.getAttribute('data-utc-time');
    element.textContent = formatLocalTime(utcTimeString);
});


document.getElementById('load-more-comments').addEventListener('click', function () {
    const button = this;
    const threadSlug = button.getAttribute('data-thread-slug');
    const offset = parseInt(button.getAttribute('data-offset'), 10);
    

    // Отправляем запрос на сервер
    fetch(`/thread/${threadSlug}/load-more-comments/?offset=${offset}`)
        .then(response => response.json())
        .then(data => {
            if (data.comments_html) {
                // Добавляем новые комментарии в контейнер
                document.getElementById('comments-container').insertAdjacentHTML('beforeend', data.comments_html);
                document.querySelectorAll('.comment-date').forEach(element => {
                    const utcTimeString = element.getAttribute('data-utc-time');
                    element.textContent = formatLocalTime(utcTimeString);
                });

                // Обновляем offset для следующей загрузки
                button.setAttribute('data-offset', offset + 25);

                // Скрываем кнопку, если больше нет комментариев
                if (!data.has_more) {
                    button.style.display = 'none';
                }
            }
        })
        .catch(error => console.error('Ошибка:', error));
});


document.addEventListener("DOMContentLoaded", function () {
    const threadId = document.getElementById("thread-id").textContent;
    const commentForm = document.getElementById("commentForm");
    const commentsContainer = document.getElementById("comments-container");

    // Редактирование
    const editMessageModal = new bootstrap.Modal(document.getElementById("editMessageModal"));
    const editMessageText = document.getElementById("editMessageText");
    const editMessageId = document.getElementById("editMessageId");
    const saveEditedMessageBtn = document.getElementById("saveEditedMessage");

    // Удаление
    const deleteModal = new bootstrap.Modal(document.getElementById("deleteModal"));
    let commentIdToDelete = null;

    // Жалобы
    const reportCommentModal = new bootstrap.Modal(document.getElementById('reportCommentModal'));
    const reportCommentIdInput = document.getElementById('reportCommentId');
    const reportReasonSelect = document.getElementById('reportReason');
    const submitReportButton = document.getElementById('submitReport');
    
    let isAuthenticated = false;

    const saveThreadChangesButton = document.getElementById('saveThreadChanges');

    function formatLocalTime(utcTimeString) {
        const date = new Date(utcTimeString);
        return date.toLocaleString('ru-RU', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
        }).replace(/\./g, '/'); // Заменяем точки на слэши
    }

    // Подключаемся к WebSocket
    const socket = new WebSocket(
        `wss://${window.location.host}/ws/thread/${threadId}/`
    );

    // Обработка входящих сообщений
    socket.onmessage = function (e) {

        const data = JSON.parse(e.data);

        if (data.action === 'auth_status') {
            // Сохраняем статус авторизации и имя пользователя
            isAuthenticated = data.is_authenticated;
            currentUsername = data.username;
        }
        if (data.action === 'update_thread') {
            const threadId = data.thread_id;
            const newContent = data.content;
    
            // Обновляем контент треда
            const threadContentElement = document.querySelector('.thread-content p');
    
            if (threadContentElement) {
                threadContentElement.textContent = newContent;
            }
        }
        if (data.action === 'new_comment') {
            updateCommentCounter(data.comment_count);
            addCommentToDOM(data.comment, isAuthenticated, currentUsername);
        } else if (data.action === 'update_comment') {
            updateCommentInDOM(data.comment);
        } else if (data.action === 'delete_comment') {
            deleteCommentFromDOM(data.comment_id);
            updateCommentCounter(data.comment_count);
        }
    };

    // Находим кнопку "Редагувати"
    const editThreadButton = document.querySelector('.btn-warning');  // Кнопка "Редагувати"

    if (editThreadButton) {
        editThreadButton.addEventListener('click', function(event) {
            event.preventDefault();

            // Находим текущий контент треда
            const threadContentElement = document.querySelector('.thread-content p');
            const currentContent = threadContentElement ? threadContentElement.innerHTML.replace(/<br\s*\/?>/g, '\n') : '';

            // Заполняем текстовое поле в модальном окне текущим контентом
            const editThreadContentInput = document.getElementById('editThreadContent');
            if (editThreadContentInput) {
                editThreadContentInput.value = currentContent;
            }

            // Открываем модальное окно
            const editThreadModal = new bootstrap.Modal(document.getElementById('editThreadModal'));
            editThreadModal.show();
        });
    }

    // Редактирование контента треда
    if (saveThreadChangesButton) {
        saveThreadChangesButton.addEventListener('click', function() {
            const newContent = document.getElementById('editThreadContent').value;

            if (newContent) {
                // Отправляем изменения через WebSocket
                socket.send(JSON.stringify({
                    action: 'edit_thread',
                    thread_id: threadId,  // ID треда
                    content: newContent
                }));

                // Закрываем модальное окно
                const editThreadModal = bootstrap.Modal.getInstance(document.getElementById('editThreadModal'));
                editThreadModal.hide();
            } else {
                alert('Контент не може бути порожнім.');
            }
        });
    }

    // Добавление комментария
    if (commentForm) {
        commentForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const content = document.getElementById("commentInput").value;

            // Отправляем данные на сервер
            socket.send(JSON.stringify({
                'action': 'add_comment',
                'content': content,
                'thread_id': threadId
            }));

            // Очищаем поле ввода
            document.getElementById("commentInput").value = '';
        });
    }

    // Открытие модального окна при редактировании
    commentsContainer.addEventListener("click", function (e) {
        if (e.target.classList.contains("edit-comment")) {
            e.preventDefault();
            const commentId = e.target.dataset.id;
            const commentContent = document.querySelector(`#comment-${commentId} .comment-content`).innerHTML.replace(/<br\s*\/?>/g, '\n');

            editMessageId.value = commentId;
            editMessageText.value = commentContent;
            editMessageModal.show();
        }
    });

    // Отправка запроса на сервер после редактирования
    saveEditedMessageBtn.addEventListener("click", function () {
        const commentId = editMessageId.value;
        const newContent = editMessageText.value.trim();

        if (newContent) {
            console.log("Отправляем отредактированный комментарий:", commentId, newContent);
            socket.send(JSON.stringify({
                'action': 'edit_comment',
                'comment_id': commentId,
                'content': newContent
            }));
            editMessageModal.hide();
        }
    });

    // Открытие модального окна при клике на кнопку удаления
    document.addEventListener("click", function (e) {
        if (e.target.classList.contains("delete-comment")) {
            e.preventDefault();
            commentIdToDelete = e.target.dataset.id; // Запоминаем ID комментария
            deleteModal.show(); // Открываем модальное окно
        }
    });

    // Обработка удаления комментария
    document.getElementById("confirmDelete").addEventListener("click", function () {
        if (commentIdToDelete) {
            socket.send(JSON.stringify({
                'action': 'delete_comment',
                'comment_id': commentIdToDelete,
                'thread_id': threadId
            }));
        }
        deleteModal.hide(); // Закрываем модальное окно
    });

    

    // Функция для добавления комментария в DOM
    function addCommentToDOM(comment) {
        const commentsContainer = document.getElementById("comments-container");
        console.log(comment)

        const commentHtml = `
            <div class="comment animate__animated animate__fadeIn" id="comment-${comment.id}">
                <div class="comment-header">
                    <div class="d-flex align-items-center">
                        <div class="message-avatar">
                            ${comment.avatar_url ? 
                                `<img src="${comment.avatar_url}" alt="${comment.author}" style="width: 40px; height: 40px; border-radius: 50%;">` 
                                : `<div>${comment.author[0].toUpperCase()}</div>`}
                        </div>
                        <div>
                            <span class="comment-author">${comment.author}</span>
                            <span class="comment-date">— ${formatLocalTime(comment.created_at)}</span>
                        </div>
                    </div>
                    ${isAuthenticated ? `
                        <div class="comment-actions">
                            <div class="dropdown">
                                <button class="dropdown-toggle" type="button" id="dropdownMenuButton${comment.id}" data-bs-toggle="dropdown" aria-expanded="false">
                                    <i class="bi bi-three-dots"></i>
                                </button>
                                <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton${comment.id}">
                                    ${comment.is_author ? `
                                        <li><a class="dropdown-item edit-comment" href="#" data-id="${comment.id}">Редагувати</a></li>
                                        <li><a class="dropdown-item delete-comment" href="#" data-id="${comment.id}">Видалити</a></li>
                                    ` : `
                                        <li><a class="dropdown-item report-comment" href="#" data-id="${comment.id}">Поскаржитися</a></li>
                                    `}
                                </ul>
                            </div>
                        </div>
                    ` : ''}
                </div>
                <p class="comment-content mt-2">${comment.content.replace(/\n/g, "<br>")}</p>
            </div>
        `;
        
        commentsContainer.insertAdjacentHTML('afterbegin', commentHtml);

        // Удаляем классы анимации после завершения
        const newComment = document.getElementById(`comment-${comment.id}`);
        newComment.addEventListener('animationend', () => {
            newComment.classList.remove('animate__animated', 'animate__fadeIn');
        });
    }

    // Функция для обновления комментария в DOM
    function updateCommentInDOM(comment) {
        const commentElement = document.getElementById(`comment-${comment.id}`);
        if (commentElement) {
            console.log("Обновляем комментарий в DOM:", comment);
            commentElement.querySelector(".comment-content").textContent = comment.content;
        }
    }

    // Функция для удаления комментария из DOM
    function deleteCommentFromDOM(commentId) {
        const commentElement = document.getElementById(`comment-${commentId}`);
        if (commentElement) {
            commentElement.remove();
        }
    }

    function updateCommentCounter(count) {
        document.querySelector(".h5.mb-3").textContent = `Коментарі (${count})`;
    }

    // Открытие модального окна при клике на кнопку "Пожаловаться"
    document.addEventListener('click', function (e) {
        if (e.target.classList.contains('report-comment')) {
            e.preventDefault();
            const commentId = e.target.dataset.id;
            reportCommentIdInput.value = commentId; // Устанавливаем ID комментария
            reportCommentModal.show(); // Открываем модальное окно
        }
    });

    // Отправка жалобы
    submitReportButton.addEventListener('click', async function () {
        const commentId = reportCommentIdInput.value;
        const reason = reportReasonSelect.value;

        if (!commentId || !reason) {
            alert('Будь ласка, оберіть причину скарги.');
            return;
        }

        try {
            const response = await fetch(`/comment/${commentId}/report/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ reason })
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.message); // "Скаргу успішно надіслано."
                reportCommentModal.hide(); // Закрываем модальное окно
            } else {
                alert(result.message); // Сообщение об ошибке
            }
        } catch (error) {
            console.error('Помилка:', error);
            alert('Сталася помилка при відправці скарги.');
        }
    });
});

