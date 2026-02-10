const inputDates = document.querySelectorAll('.input-date');

const dataFormatada = new Date().toISOString().split('T')[0];

inputDates.forEach(input => {
  input.value = dataFormatada;
});