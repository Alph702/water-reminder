self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(clients.claim());
});

// Function to show notification
function showNotification(title, message) {
    self.registration.showNotification(title, {
        body: message,
        icon: '/static/230x0w.png',
        requireInteraction: true
    });
}

// Listen for push messages
self.addEventListener('push', (event) => {
    const data = event.data.json();
    showNotification(data.title, data.message);
});

// Check water intake every hour
setInterval(() => {
    fetch('/get_all_stats')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.all_users_stats.length > 0) {
                data.all_users_stats.forEach(user => {
                    if (user.remaining > 0) {
                        showNotification(
                            'Hourly Water Reminder',
                            `Hey ${user.username}! You still need ${user.remaining}ml to reach your daily goal.`
                        );
                    }
                });
            }
        });
}, 3600000); // Check every hour
