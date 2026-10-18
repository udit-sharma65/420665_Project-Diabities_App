document.addEventListener("DOMContentLoaded", function () {
  var apply = document.getElementById("bmi-apply");
  if (!apply) {
    return;
  }
  apply.addEventListener("click", function () {
    var height = parseFloat(document.getElementById("height-cm").value);
    var weight = parseFloat(document.getElementById("weight-kg").value);
    var output = document.getElementById("bmi-output");
    if (!height || !weight || height <= 0 || weight <= 0) {
      output.textContent = "Enter both height and weight.";
      return;
    }
    var bmi = weight / Math.pow(height / 100, 2);
    document.getElementById("bmi").value = bmi.toFixed(1);
    output.textContent = "Your BMI is " + bmi.toFixed(1) + ".";
  });
});
