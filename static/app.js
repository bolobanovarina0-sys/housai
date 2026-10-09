let myChart = null;

document.getElementById("loadBtn").addEventListener("click", async () => {
  const id = document.getElementById("aptIdInput").value.trim();
  if (!id) return alert("Введите ID квартиры!");

  try {
    const response = await fetch(`/api/apartment?id=${encodeURIComponent(id)}`);
    const data = await response.json();
    if (data.error) return alert(data.error);

    // Отрисовка плана
    const img = document.getElementById("planImg");
    const placeholder = document.getElementById("placeholderText");
    const overlay = document.getElementById("pinsOverlay");

    img.src = data.plan_url;
    img.style.display = "block";
    placeholder.style.display = "none";
    overlay.innerHTML = "";

    img.onload = () => {
      const rect = img.getBoundingClientRect();
      const containerRect = overlay.getBoundingClientRect();
      const offsetX = (containerRect.width - rect.width) / 2;
      const offsetY = (containerRect.height - rect.height) / 2;

      data.sensors.forEach(s => {
        const pin = document.createElement("div");
        pin.className = "sensor-pin " + (s.type === 'temperature' ? 'danger' : s.type === 'leak' ? 'primary' : 'success');
        pin.style.left = (offsetX + (s.x / 100) * rect.width) + "px";
        pin.style.top = (offsetY + (s.y / 100) * rect.height) + "px";
        pin.innerHTML = `<span>${s.name}: <b>${s.value} ${s.unit}</b></span>`;
        overlay.appendChild(pin);
      });
    };

    // Обновление цифр и графика
    const totalCost = data.forecast.values.reduce((a, b) => a + b, 0);
    document.getElementById("costVal").innerText = totalCost + " ₽";
    
    const reportBtn = document.getElementById("reportBtn");
    reportBtn.disabled = false;
    reportBtn.dataset.aptId = id;

    const ctx = document.getElementById("forecastChart").getContext("2d");
    if (myChart) myChart.destroy();
    myChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: data.forecast.labels,
        datasets: [{ label: 'Расход (₽)', data: data.forecast.values, backgroundColor: '#38bdf8', borderRadius: 4 }]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });

  } catch (err) {
    alert("Ошибка соединения с сервером.");
  }
});

document.getElementById("reportBtn").addEventListener("click", (e) => {
  const id = e.target.dataset.aptId;
  if (id) window.open(`/api/apartment/report?id=${id}`, '_blank');
});
