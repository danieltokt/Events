async function getEvents() {
  try {
    return await apiGetEvents();
  } catch (error) {
    showNotification(error.message, "error");
    throw error;
  }
}

// Get single event
async function getEvent(id) {
  try {
    return await apiGetEvent(id);
  } catch (error) {
    showNotification(error.message, "error");
    throw error;
  }
}

// Create event
async function createEvent(eventData) {
  try {
    const event = await apiCreateEvent(eventData);
    showNotification("Событие успешно создано!", "success");
    setTimeout(() => window.location.href = "events.html", 1000);
    return event;
  } catch (error) {
    const formError = document.getElementById("formError");
    if (formError) formError.textContent = error.message;
    showNotification(error.message, "error");
    throw error;
  }
}

// Update event
async function updateEvent(id, eventData) {
  try {
    return await apiUpdateEvent(id, eventData);
  } catch (error) {
    const formError = document.getElementById("formError");
    if (formError) formError.textContent = error.message;
    
    // ✅ Проверка на ошибку прав доступа
    if (error.response?.status === 403) {
      showNotification("Вы не можете редактировать это событие", "error");
    } else {
      showNotification(error.message, "error");
    }
    throw error;
  }
}

// Delete event
async function deleteEvent(id) {
  try {
    await apiDeleteEvent(id);
    showNotification("Событие удалено", "info");
  } catch (error) {
    // ✅ Проверка на ошибку прав доступа
    if (error.response?.status === 403) {
      showNotification("Вы не можете удалить это событие", "error");
    } else {
      showNotification(error.message, "error");
    }
    throw error;
  }
}

// ✅ Проверка прав: может ли пользователь редактировать событие
function canEditEvent(event) {
  if (!event) return false;
  
  const user = getCurrentUser();
  
  // Если пользователь не авторизован
  if (!user) return false;
  
  // Только создатель может редактировать
  return event.created_by === user.id;
}

// ✅ Показать/скрыть кнопки редактирования и удаления
function updateEventActionButtons(event, containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;
  
  // Найти кнопки действий
  const editBtn = container.querySelector('.btn-edit-event');
  const deleteBtn = container.querySelector('.btn-delete-event');
  
  // Скрыть кнопки если пользователь не создатель
  if (!canEditEvent(event)) {
    if (editBtn) editBtn.style.display = 'none';
    if (deleteBtn) deleteBtn.style.display = 'none';
  } else {
    // Показать кнопки если пользователь создатель
    if (editBtn) editBtn.style.display = 'inline-block';
    if (deleteBtn) deleteBtn.style.display = 'inline-block';
  }
}

// ✅ Функция для удаления события с подтверждением
async function confirmDeleteEvent(eventId, eventTitle) {
  const confirmed = confirm(
    `Вы уверены, что хотите удалить событие "${eventTitle}"?`
  );
  
  if (confirmed) {
    try {
      await deleteEvent(eventId);
      // Перезагрузить список событий
      setTimeout(() => window.location.href = 'events.html', 1500);
    } catch (error) {
      // Ошибка уже показана в deleteEvent()
      console.error('Delete error:', error);
    }
  }
}

// ✅ Проверить права перед редактированием
function checkEditPermission(event) {
  if (!canEditEvent(event)) {
    showNotification("Вы не можете редактировать это событие", "error");
    return false;
  }
  return true;
}

// ✅ Отрендерить событие в списке
function renderEventCard(event) {
  const user = getCurrentUser();
  const isOwner = canEditEvent(event);
  
  // Кнопки будут видны только если пользователь создатель
  const actionButtons = isOwner ? `
    <button class="btn btn-sm btn-edit-event" 
            onclick="if (checkEditPermission(${JSON.stringify(event).replace(/"/g, '&quot;')})) 
                      window.location.href='edit-event.html?id=${event.id}'">
      Редактировать
    </button>
    <button class="btn btn-sm btn-danger btn-delete-event" 
            onclick="confirmDeleteEvent(${event.id}, '${event.title.replace(/'/g, "\\'")}')">
      Удалить
    </button>
  ` : '';
  
  return `
    <div class="event-card">
      <h3>${event.title}</h3>
      <p>${event.description}</p>
      <p><strong>Место:</strong> ${event.location || 'Не указано'}</p>
      <p><strong>Дата:</strong> ${new Date(event.start_date).toLocaleString('ru-RU')}</p>
      <p><strong>Создатель:</strong> ${event.created_by_username || 'Неизвестно'}</p>
      <div class="event-actions">
        <button class="btn btn-primary" onclick="registerForEvent(${event.id})">
          Зарегистрироваться
        </button>
        ${actionButtons}
      </div>
    </div>
  `;
}