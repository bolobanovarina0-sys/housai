/**
 * Модуль клиентской логики: Цифровой двойник квартиры (IoT & ЖКХ)
 * Проект: Всероссийский конкурс «Молодые строители России»
 */

let forecastChartInstanceApt = null;

document.addEventListener("DOMContentLoaded", () => {
  const loadBtn = document.getElementById("loadApartmentBtn");
  const exportBtn = document.getElementById("exportReportBtn");

  if (loadBtn) {
    loadBtn.addEventListener("click", () => {
      const aptId = document.getElementById("apartmentIdInput").value.trim();
      if (aptId) {
        fetchApartmentData(aptId);
      } else {
        alert("Пожалуйста, введите ID квартиры.");
      }
    });
  }

  if (exportBtn) {
    exportBtn.addEventListener("click", (e) => {
      const aptId = e.target.dataset.aptId;
      if (aptId) {
        window.open(`/api/apartment/report?id=${encodeURIComponent(aptId)}`, "_blank");
      }
    });
  }
});

/**
 * Запрос данных цифрового двойника квартиры с бэкенда
 * @param {string} id - Учетный ID объекта
 */
async function fetchApartmentData(id) {
  try {
    const response = await fetch(`/api/apartment?id=${encodeURIComponent(id)}`);
    const data = await response.json();

    if (data.error) {
      alert(`Ошибка: ${data.error}`);
      return;
    }

    renderApartmentPlan(data.plan_url, data.sensors);
    updateAnalyticsAndChart(data.forecast, id);

  } catch (error) {
    console.error("Ошибка при получении данных квартиры:", error);
    alert("Не удалось связаться с сервером телеметрии.");
  }
}

/**
 * Отрисовка плана помещения и размещение датчиков с абсолютным позиционированием
 * @param {string} planUrl - URL или SVG-код схемы
 * @param {Array} sensors - Массив датчиков телеметрии
 */
function renderApartmentPlan(planUrl, sensors) {
  const img = document.getElementById("apartmentPlanImg");
  const placeholder = document.getElementById("planPlaceholder");
  const overlay = document.getElementById("sensorPinsOverlay");
  const badge = document.getElementById("apartmentStatusBadge");

  img.src = planUrl;
  img.style.display = "block";
  placeholder.style.display = "none";
  
  if (badge) {
    badge.textContent = "ОНЛАЙН (IOT)";
    badge.classList.add("ok-pill");
  }

  overlay.innerHTML = "";

  // Ожидание загрузки изображения для точного расчета координат пинов
  img.onload = () => {
    const rect = img.getBoundingClientRect();
    const containerRect = overlay.getBoundingClientRect();

    const offsetX = (containerRect.width - rect.width) / 2;
    const offsetY = (containerRect.height - rect.height) / 2;

    sensors.forEach(sensor => {
      const pin = document.createElement("div");
      pin.className = "sensor-pin";
      
      // Цветовая индикация в зависимости от типа датчика
      if (sensor.type === "temperature") {
        pin.style.background = "var(--danger)";
      } else if (sensor.type === "leak") {
        pin.style.background = "var(--primary)";
      } else {
        pin.style.background = "var(--ok)";
      }

      // Позиционирование в процентах относительно размеров плана
      pin.style.position = "absolute";
      pin.style.left = (offsetX + (sensor.x / 100) * rect.width) + "px";
      pin.style.top = (offsetY + (sensor.y / 100) * rect.height) + "px";

      // Всплывающая плашка со значением
      const label = document.createElement("div");
      label.innerHTML = `<b>${sensor.name.split(' ')[0]}: ${sensor.value} ${sensor.unit}</b>`;
      label.style.position = "absolute";
      label.style.top = "-24px";
      label.style.left = "16px";
      label.style.background = "rgba(15, 23, 42, 0.9)";
      label.style.color = "#fff";
      label.style.padding = "2px 6px";
      label.style.borderRadius = "4px";
      label.style.fontSize = "10px";
      label.style.whiteSpace = "nowrap";
      label.style.border = "1px solid var(--border-color)";

      pin.appendChild(label);
      overlay.appendChild(pin);
    });
  };
}

/**
 * Обновление аналитики и построение графика прогноза расходов (Chart.js)
 * @param {Object} forecast - Данные прогноза (метки дней и значения)
 * @param {string} aptId - ID квартиры
 */
function updateAnalyticsAndChart(forecast, aptId) {
  const totalCost = forecast.values.reduce((a, b) => a + b, 0);
  const costValElem = document.getElementById("forecastCostVal");
  if (costValElem) {
    costValElem.textContent = `${totalCost.toLocaleString('ru-RU')} ₽`;
  }

  const exportBtn = document.getElementById("exportReportBtn");
  if (exportBtn) {
    exportBtn.disabled = false;
    exportBtn.dataset.aptId = aptId;
  }

  const canvasCtx = document.getElementById("forecastChartApt");
  if (!canvasCtx) return;

  const ctx = canvasCtx.getContext("2d");
  if (forecastChartInstanceApt) {
    forecastChartInstanceApt.destroy();
  }

  forecastChartInstanceApt = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: forecast.labels,
      datasets: [{
        label: 'Прогноз расходов (₽)',
        data: forecast.values,
        backgroundColor: '#38bdf8',
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { grid: { display: false } },
        y: { grid: { color: '#334155' } }
      }
    }
  });
}
