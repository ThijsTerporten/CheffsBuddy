$(document).ready(function(){
    $('.sidenav').sidenav({edge: "right"});
    $("select").formSelect();
    $(".tooltipped").tooltip();
  });

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

$("#addInstruction").on("click", ".btn-remove", function(e){
  e.preventDefault(e);
  $(this).parent("div").remove();
  directions--;
})