// Ініціалізація карти
function initMap(elementId, initialView = [0, 0], zoom = 2) {
    var map = L.map(elementId).setView(initialView, zoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    return map;
}

// Додавання точок для шашлику на карту
function addKebabSpots(map, spots) {
    spots.forEach(function(spot) {
        var latlng = spot.fields.location.match(/-?\d+\.\d+/g);
        L.marker([parseFloat(latlng[1]), parseFloat(latlng[0])])
            .addTo(map)
            .bindPopup(spot.fields.name);
    });
}

// Отримання точок для шашлику з сервера
function fetchKebabSpots(url, lat, lng, callback) {
    $.ajax({
        url: `${url}?lat=${lat}&lng=${lng}`,
        method: 'GET',
        success: function(data) {
            var kebabSpots = JSON.parse(data);
            callback(kebabSpots);
        }
    });
}

function initMapWithUserLocation(map, url, callback) {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var lat = position.coords.latitude;
            var lng = position.coords.longitude;
            map.setView([lat, lng], 13);

            // Створюємо червону іконку для маркера
            var redIcon = new L.Icon({
                iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                iconSize: [25, 41],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [41, 41]
            });

            // Додаємо червоний маркер "Ви тут"
            L.marker([lat, lng], {icon: redIcon}).addTo(map)
                .bindPopup('Ви тут')
                .openPopup();

            fetchKebabSpots(url, lat, lng, function(spots) {
                addKebabSpots(map, spots);
                if (callback) callback(map, lat, lng);
            });
        }, function(error) {
            console.error("Geolocation error: ", error);
        });
    } else {
        console.error("Geolocation is not available");
    }
}