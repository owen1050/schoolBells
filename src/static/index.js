//var id = new URLSearchParams(window.location.search).get('id')
//how to get url param

let countdownInterval;
let shiftTimerAheadSeconds = 0;

function initIndex() {
  preloadTimesFromURL();   
  startCountdownToNextTime();
  attachInputListeners();
}

function attachInputListeners() {
  for (let i = 1; i <= 24; i++) {
    const timeInput = document.getElementById(`time${i}`);
    const eventInput = document.getElementById(`event${i}`);

    if (timeInput) {
      timeInput.addEventListener('input', startCountdownToNextTime);
    }
    if (eventInput) {
      eventInput.addEventListener('input', startCountdownToNextTime);
    }
  }
}


function preloadTimesFromURL() {
  const params = new URLSearchParams(window.location.search);

  for (let i = 1; i <= 24; i++) {
    const timeKey = `time${i}`;
    const eventKey = `event${i}`;

    const timeVal = params.get(timeKey);
    const eventVal = params.get(eventKey);

    if (timeVal && /^\d{2}:\d{2}$/.test(timeVal)) {
      const timeInput = document.getElementById(timeKey);
      if (timeInput) timeInput.value = timeVal;
    }

    if (eventVal) {
      const eventInput = document.getElementById(eventKey);
      if (eventInput) eventInput.value = decodeURIComponent(eventVal);
    }
  }
}



function startCountdownToNextTime() {
  const next = getNextUpcomingTime();
  const timerElement = document.getElementById('timer');
  const eventDisplay = document.getElementById('eventDisplay');

  if (!next) {
    timerElement.textContent = '--:--';
    eventDisplay.textContent = '';
    timerElement.classList.remove('warning');
    if (countdownInterval) clearInterval(countdownInterval);
    return;
  }

  // Set event label
  eventDisplay.textContent = next.event ? next.event : '';

  if (countdownInterval) clearInterval(countdownInterval);

  countdownInterval = setInterval(() => {
    const now = new Date();

    // FIX: use next.time instead of next
    const diffMs = (next.time - now) - shiftTimerAheadSeconds * 1000;

    if (diffMs <= 0) {
      clearInterval(countdownInterval);
      timerElement.textContent = '00:00';
      timerElement.classList.add('warning');
      startCountdownToNextTime();
      return;
    }

    const totalSeconds = Math.floor(diffMs / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;

    timerElement.textContent = `${pad(minutes)}:${pad(seconds)}`;

    if (totalSeconds <= 60) {
      timerElement.classList.add('warning');
    } else {
      timerElement.classList.remove('warning');
    }
  }, 1000);
}


function getNextUpcomingTime() {
  const now = new Date();
  now.setSeconds(now.getSeconds() + shiftTimerAheadSeconds);
  const times = [];

  for (let i = 1; i <= 24; i++) {
    const timeStr = (document.getElementById(`time${i}`)?.value || "").trim();
    const eventStr = (document.getElementById(`event${i}`)?.value || "").trim();

    if (!/^\d{2}:\d{2}$/.test(timeStr)) continue;

    const [hour, minute] = timeStr.split(':').map(Number);
    const timeDate = new Date();
    timeDate.setHours(hour, minute, 0, 0);

    if (timeDate <= now) {
      timeDate.setDate(timeDate.getDate() + 1);
    }

    times.push({ time: timeDate, event: eventStr });
  }

  if (times.length === 0) return null;

  times.sort((a, b) => a.time - b.time);
  return times[0];
}


function pad(num) {
  return num.toString().padStart(2, '0');
}
