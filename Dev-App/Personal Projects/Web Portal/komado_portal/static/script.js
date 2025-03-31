document.addEventListener('DOMContentLoaded', function() {
    // Notification System
    initializeNotifications();
    
    // Project Management
    initializeProjectManagement();
    
    // Task Management
    initializeTaskManagement();
});

function initializeNotifications() {
    const notificationBell = document.querySelector('.notification-bell');
    const notificationDropdown = document.querySelector('.notification-dropdown');
    const notificationList = document.querySelector('.notification-list');
    const notificationCount = document.querySelector('.notification-count');

    notificationBell?.addEventListener('click', function() {
        notificationDropdown.style.display = notificationDropdown.style.display === 'block' ? 'none' : 'block';
        if (notificationDropdown.style.display === 'block') {
            fetchNotifications();
        }
    });

    document.addEventListener('click', function(e) {
        if (notificationBell && !notificationBell.contains(e.target)) {
            notificationDropdown.style.display = 'none';
        }
    });

    setInterval(fetchNotifications, 30000);
    fetchNotifications();

    function fetchNotifications() {
        fetch('/notifications')
            .then(response => response.json())
            .then(notifications => {
                notificationCount.textContent = notifications.length;
                notificationList.innerHTML = notifications.map(notification => `
                    <div class="notification-item" data-id="${notification.id}">
                        <p>${notification.message}</p>
                        <small>${notification.created_at}</small>
                    </div>
                `).join('');

                document.querySelectorAll('.notification-item').forEach(item => {
                    item.addEventListener('click', function() {
                        markAsRead(this.dataset.id);
                        this.remove();
                        notificationCount.textContent = parseInt(notificationCount.textContent) - 1;
                    });
                });
            });
    }
}

function initializeProjectManagement() {
    const editProjectModal = document.getElementById('editProjectModal');
    const taskModal = document.getElementById('taskModal');
    const closeButtons = document.getElementsByClassName('close');

    document.getElementById('editProjectForm')?.addEventListener('submit', function(e) {
        e.preventDefault();
        const projectId = this.getAttribute('data-project-id');
        const formData = new FormData(this);

        fetch(`/edit_project/${projectId}`, {
            method: 'POST',
            body: formData
        }).then(() => window.location.reload());
    });

    Array.from(closeButtons).forEach(button => {
        button.onclick = function() {
            editProjectModal.style.display = 'none';
            taskModal.style.display = 'none';
        }
    });

    window.onclick = function(event) {
        if (event.target == editProjectModal || event.target == taskModal) {
            editProjectModal.style.display = 'none';
            taskModal.style.display = 'none';
        }
    }
}

function initializeTaskManagement() {
    const taskItems = document.querySelectorAll('.task-item');
    const taskColumns = document.querySelectorAll('.task-column');

    taskItems.forEach(task => {
        task.addEventListener('dragstart', () => task.classList.add('dragging'));
        task.addEventListener('dragend', () => task.classList.remove('dragging'));
    });

    taskColumns.forEach(column => {
        column.addEventListener('dragover', e => {
            e.preventDefault();
            const draggingTask = document.querySelector('.dragging');
            if (draggingTask) {
                column.appendChild(draggingTask);
                updateTaskStatus(draggingTask.dataset.taskId, column.dataset.status);
            }
        });
    });
}

// Utility Functions
function editProject(projectId) {
    const projectCard = document.querySelector(`.project-card[data-project-id="${projectId}"]`);
    if (!projectCard) return;

    const title = projectCard.querySelector('h3').textContent;
    const description = projectCard.querySelector('p').textContent;
    const status = projectCard.querySelector('.project-status').textContent.split(': ')[1];

    document.querySelector('#editProjectForm input[name="title"]').value = title;
    document.querySelector('#editProjectForm textarea[name="description"]').value = description;
    document.querySelector('#editProjectForm select[name="status"]').value = status;
    
    document.getElementById('editProjectForm').setAttribute('data-project-id', projectId);
    document.getElementById('editProjectModal').style.display = 'block';
}

function deleteProject(projectId) {
    if (confirm('Are you sure you want to delete this project?')) {
        fetch(`/delete_project/${projectId}`, {
            method: 'GET',
        }).then(() => window.location.reload());
    }
}

function showAddTaskForm(projectId) {
    const form = document.getElementById('addTaskForm');
    form.setAttribute('data-project-id', projectId);
    document.getElementById('taskModal').style.display = 'block';
}

function markAsRead(notificationId) {
    fetch(`/notifications/mark-read/${notificationId}`);
}

function updateTaskStatus(taskId, status) {
    fetch(`/update_task_status/${taskId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: status })
    });
}