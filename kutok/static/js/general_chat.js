document.addEventListener("DOMContentLoaded", function() {
    const chatMessages = document.getElementById('chat-messages');

    // Инициализация всех выпадающих списков на странице
    var dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    var dropdownList = dropdownElementList.map(function (dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl);
    });

    const scrollToBottomBtn = document.getElementById('scroll-to-bottom');
    chatMessages.addEventListener('scroll', () => {
        if (!isUserAtBottom(chatMessages)) {
            scrollToBottomBtn.classList.add('visible'); // Показываем кнопку
        } else {
            scrollToBottomBtn.classList.remove('visible'); // Скрываем кнопку
        }
    });

    scrollToBottomBtn.addEventListener('click', () => {
        chatMessages.scrollTo({
            top: chatMessages.scrollHeight,
            behavior: 'smooth' // Плавная прокрутка
        });
        scrollToBottomBtn.classList.remove('visible'); // Скрываем кнопку после прокрутки
    });

    // Функция для форматирования времени в локальное время пользователя
    function formatLocalTime(timestamp) {
        const date = new Date(timestamp);  // Преобразуем строку в объект Date
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });  // Форматируем время
    }

    function isUserAtBottom(container, threshold = 175) {
        if (!container) {
            console.error('Контейнер чата не найден');
            return false;
        }
        const scrollTop = container.scrollTop;
        const scrollHeight = container.scrollHeight;
        const clientHeight = container.clientHeight;
        const difference = Math.abs(scrollHeight - (scrollTop + clientHeight));
        // Отладка: выводим значения для проверки
        console.log('scrollTop:', scrollTop);
        console.log('scrollHeight:', scrollHeight);
        console.log('clientHeight:', clientHeight);
        console.log('Разница:', difference);

        return difference <= threshold;
    }

    // Обновляем время для всех сообщений при загрузке страницы
    const messages = chatMessages.querySelectorAll('.message');
    messages.forEach(message => {
        const timestamp = message.getAttribute('data-timestamp');
        const timeElement = message.querySelector('.message-time');
        if (timestamp && timeElement) {
            timeElement.textContent = formatLocalTime(timestamp);
        }
    });

    const chatSocket = new WebSocket(
        'wss://' + window.location.host + '/ws/chat/'
    );

    const chatMessageInput = document.getElementById('chat-message-input');
    const chatMessageSubmit = document.getElementById('chat-message-submit');

    // Прокрутка вниз при загрузке страницы
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Функция для добавления нового сообщения в окно чата
    function addMessage(message, user, userId, timestamp, isAuthor, isAuthenticated, messageId) {
        // Формируем HTML-код для сообщения
        const messageHTML = `
            <div class="message ${isAuthor ? 'user' : 'bot'}" data-message-id="${messageId}" data-timestamp="${timestamp}">
                <div class="message-avatar">${user ? user[0].toUpperCase() : 'A'}</div>
                <div class="message-content">
                    ${isAuthenticated ? `
                        <div class="message-actions">
                            <div class="dropdown">
                                <button class="btn btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                                    <i class="bi bi-three-dots"></i>
                                </button>
                                <ul class="dropdown-menu">
                                    ${isAuthor ? `
                                        <li><a class="dropdown-item edit-message" href="#"><i class="bi bi-pencil me-2"></i>Редактировать</a></li>
                                        <li><a class="dropdown-item delete-message" href="#"><i class="bi bi-trash me-2"></i>Удалить</a></li>
                                    ` : ''}
                                    ${!isAuthor ? `
                                        <li><a class="dropdown-item report-message" href="#"><i class="bi bi-flag me-2"></i>Пожаловаться</a></li>
                                    ` : ''}
                                </ul>
                            </div>
                        </div>
                    ` : ''}
                    <div class="message-author">${user || 'Anonymous'}</div>
                    <div class="message-text">${message}</div>
                    <span class="message-time">${formatLocalTime(timestamp)}</span>
                </div>
            </div>
        `;

        // Добавляем сообщение в конец списка
        chatMessages.insertAdjacentHTML('beforeend', messageHTML);

        // Проверяем, находится ли пользователь внизу
        if (isUserAtBottom(chatMessages)) {
            // Прокручиваем вниз, если пользователь внизу
            // setTimeout(() => {
            //     chatMessages.scrollTo({
            //         top: chatMessages.scrollHeight,
            //         behavior: 'smooth' // Плавная прокрутка
            //     });
            // }, 100); // Задержка 100 мс
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        // chatMessages.scrollTop = chatMessages.scrollHeight;

         // Плавное появление нового сообщения
        const newMessage = chatMessages.lastElementChild;
        setTimeout(() => {
            newMessage.classList.add('visible');
        }, 100); // Небольшая задержка для запуска анимации


        // Инициализация выпадающего списка для нового сообщения
        if (isAuthenticated) {
            const newDropdownToggle = chatMessages.lastElementChild.querySelector('.dropdown-toggle');
            if (newDropdownToggle) {
                new bootstrap.Dropdown(newDropdownToggle);
            }
        }
    }

    // Обработчик для кнопки "Редактировать" (для всех сообщений)
    document.addEventListener('click', function(event) {
        if (event.target.closest('.dropdown-item.edit-message')) {
            const messageElement = event.target.closest('.message');
            const messageId = messageElement.dataset.messageId; // Получаем ID сообщения
            const messageText = messageElement.querySelector('.message-text').innerText.trim();

            // Заполняем форму в модальном окне
            document.getElementById('editMessageId').value = messageId;
            document.getElementById('editMessageText').value = messageText;

            // Открываем модальное окно
            const editModal = new bootstrap.Modal(document.getElementById('editMessageModal'));
            editModal.show();
        }
    });

    // Обработчик для кнопки "Сохранить" в модальном окне
    document.getElementById('saveEditedMessage').addEventListener('click', function() {
        const messageId = document.getElementById('editMessageId').value;
        const newMessage = document.getElementById('editMessageText').value;

        if (newMessage.trim()) {
            // Отправляем данные на сервер
            chatSocket.send(JSON.stringify({
                'action': 'edit_message',
                'message_id': messageId,
                'new_message': newMessage
            }));

            // Закрываем модальное окно
            const editModal = bootstrap.Modal.getInstance(document.getElementById('editMessageModal'));
            editModal.hide();
        }
    });

    // Обработчик для кнопки "Удалить" (для всех сообщений)
    document.addEventListener('click', function(event) {
        if (event.target.closest('.dropdown-item.delete-message')) {
            const messageElement = event.target.closest('.message');
            const messageId = messageElement.dataset.messageId; // Получаем ID сообщения

            // Сохраняем ID сообщения в модальном окне
            document.getElementById('deleteMessageModal').dataset.messageId = messageId;

            // Открываем модальное окно
            const deleteModal = new bootstrap.Modal(document.getElementById('deleteMessageModal'));
            deleteModal.show();
        }
    });

    // Обработчик для кнопки "Удалить" в модальном окне
    document.getElementById('confirmDeleteMessage').addEventListener('click', function() {
        const messageId = document.getElementById('deleteMessageModal').dataset.messageId;

        if (messageId) {
            // Отправляем запрос на сервер для удаления сообщения
            chatSocket.send(JSON.stringify({
                'action': 'delete_message',
                'message_id': messageId
            }));

            // Закрываем модальное окно
            const deleteModal = bootstrap.Modal.getInstance(document.getElementById('deleteMessageModal'));
            deleteModal.hide();
        }
    });


    // Обработчик для кнопки "Пожаловаться"
    document.addEventListener('click', function(event) {
        if (event.target.closest('.dropdown-item.report-message')) {
            const messageElement = event.target.closest('.message');
            const messageId = messageElement.dataset.messageId; // Получаем ID сообщения

            // Сохраняем ID сообщения в модальном окне
            document.getElementById('reportMessageId').value = messageId;

            // Открываем модальное окно
            const reportModal = new bootstrap.Modal(document.getElementById('reportMessageModal'));
            reportModal.show();
        }
    });

    // Обработчик для кнопки "Отправить жалобу"
    document.getElementById('submitReport').addEventListener('click', function() {
        const messageId = document.getElementById('reportMessageId').value;
        const reason = document.getElementById('reportReason').value;

        if (messageId && reason) {
            // Отправляем данные на сервер
            chatSocket.send(JSON.stringify({
                'action': 'report_message',
                'message_id': messageId,
                'reason': reason
            }));

            // Закрываем модальное окно
            const reportModal = bootstrap.Modal.getInstance(document.getElementById('reportMessageModal'));
            reportModal.hide();

            // Оповещаем пользователя
            alert('Жалоба отправлена. Спасибо за вашу бдительность!');
        }
    });


    // Обработчик получения сообщений от сервера
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log('Получено сообщение от сервера:', data); // Отладка

        if (data.action === 'send_message') {
            addMessage(
                data.message,
                data.user,
                data.user_id,
                data.timestamp,
                data.current_user_is_author,
                data.is_authenticated,
                data.message_id // Передаём message_id
            );
            // Воспроизведение звука получения сообщения, если сообщение не от вас
            // if (!data.current_user_is_author) {
            //     document.getElementById('receive-sound').play();
            // }
            let notificationSound;
            if (data.current_user_is_author) {
                // Звук для автора комментария
                notificationSound = new Audio('/static/sounds/sent_comment.mp3');
            } else {
                // Звук для остальных пользователей
                notificationSound = new Audio('/static/sounds/received_comment.wav');
            }
            notificationSound.play();
        } else if (data.action === 'edit_message') {
            const messageElement = document.querySelector(`.message[data-message-id="${data.message_id}"]`);
            if (messageElement) {
                // Обновляем текст сообщения
                const messageTextElement = messageElement.querySelector('.message-text');
                messageTextElement.innerText = data.new_message;
            }
        } else if (data.action === 'delete_message') {
            const messageElement = document.querySelector(`.message[data-message-id="${data.message_id}"]`);
            if (messageElement) {
                // Удаляем элемент сообщения из DOM
                messageElement.remove();
                console.log(`Сообщение ${data.message_id} удалено из интерфейса`); // Отладка
            } else {
                console.error(`Сообщение ${data.message_id} не найдено в DOM`); // Отладка
            }
        } else if (data.action === 'report_confiramtion') {
            // Уведомляем пользователя
            alert(data.message);
        }

    };

    // Обработчик закрытия соединения
    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly');
    };

    // Обработчик отправки сообщения
    if (chatMessageInput && chatMessageSubmit) {
        chatMessageSubmit.onclick = function(e) {
            const message = chatMessageInput.value;
            if (message) {
                chatSocket.send(JSON.stringify({
                    'action': 'send_message',
                    'message': message
                }));
                chatMessageInput.value = '';
                console.log('Отправка сообщения:', message); // Отладка

                // Прокрутка вниз при отправке сообщения
                setTimeout(() => {
                    chatMessages.scrollTo({
                        top: chatMessages.scrollHeight,
                        behavior: 'smooth' // Плавная прокрутка
                    });
                }, 100); // Задержка 100 мс
                console.log('Прокрутка вниз при отправке сообщения'); // Отладка

                // Воспроизведение звука отправки сообщения
                // document.getElementById('send-sound').play();
            }
        };
        // Обработчик нажатия Enter в поле ввода
        chatMessageInput.onkeypress = function(e) {
            if (e.keyCode === 13) {  // Enter key
                chatMessageSubmit.click();
            }
        };
    }

    
});
