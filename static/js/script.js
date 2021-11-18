$(document).ready(function(){
    $('.sidenav').sidenav({edge: "right"});
    $("select").formSelect();
    $(".tooltipped").tooltip();
  });


// Add extra input fields in the form

let ingredients = 1;
let maxIngredients = 25;
let directions = 1;
let maxDirections = 40;
  $("#add-dir-btn").click(function(e) {
    e.preventDefault();
    $("#addInstruction").append(
      `
      <div class="input-field">
          <label for="instructions">
              Recipe Instructions
          </label>
          <input type="text" name="instructions" required>
          <button class="btn-remove right" type="button"><i class="fas fa-trash-alt"></i></button>
      </div>`);
      directions++;
  });


$("#add-ingr-btn").click(function(e) {
  e.preventDefault();
  $("addIngredient").append(
    `
    <div class="input-field">
    <label for="ingredients">
        Recipe Ingredients
    </label>
    <input type="text" name="ingredients" required>
    <button class="btn-remove right" type="button"><i class="fas fa-trash-alt"></i></button>
</div>`
  );
  ingredients++;
});

//  Remove created input fields in the form
$("#addInstruction").on("click", ".btn-remove", function(e){
  e.preventDefault(e);
  $(this).parent("div").remove();
  directions--;
});