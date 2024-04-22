self.addEventListener('install', function(event) {
    console.log('Service Worker instalado');
 });
 
 self.addEventListener('activate', function(event) {
    console.log('Service Worker ativado');
 });
 
 self.addEventListener('push', function(event) {
    console.log('Notificação recebida:', event.data.text());
 
    const title = 'Título da Notificação';
    const options = {
        body: event.data.text()
    };
 
    event.waitUntil(self.registration.showNotification(title, options));
 });
 