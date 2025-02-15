const express = require('express');
const path = require('path');
const http = require('http');
const WebSocket = require('ws');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

let occupancy = 50;
let accessibleSeats = 1; // Inicialmente, 1 de 2 plazas disponibles

// Middleware para servir archivos estáticos
app.use(express.static(__dirname));

// Middleware para parsear datos del formulario (POST)
app.use(express.urlencoded({ extended: true }));

// Ruta principal: vista del bus
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// WebSocket: enviar datos iniciales al conectarse
wss.on('connection', (ws) => {
  ws.send(JSON.stringify({ type: 'occupancy', value: occupancy }));
  ws.send(JSON.stringify({ type: 'accessibility', available: accessibleSeats, total: 2 }));
});

// Ruta para actualizar la información desde el panel de administración
app.post('/admin/update', (req, res) => {
  occupancy = parseInt(req.body.percentage);
  accessibleSeats = parseInt(req.body.accessibleSeats);
  // Enviar los nuevos datos a todos los clientes conectados vía WebSocket
  wss.clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify({ type: 'occupancy', value: occupancy }));
      client.send(JSON.stringify({ type: 'accessibility', available: accessibleSeats, total: 2 }));
    }
  });
  res.send('Actualizado correctamente');
});

// Ruta para acceder al panel de administración
app.get('/admin', (req, res) => {
  res.sendFile(path.join(__dirname, 'admin.html'));
});

server.listen(3000, () => {
  console.log('Servidor corriendo en puerto 3000');
});
