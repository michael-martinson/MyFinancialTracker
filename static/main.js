
$(document).ready(function () {
    $(".btn-addspending").on(
        "click", 
        { html: form_addspending, type: "addspending" },
        append_form,
    );
    $(".btn-addexpense").on(
        "click",
        { html: form_addexpense, type: "addexpense" },
        append_form,
    ) 
    $(".btn-adddebt").on(
        "click",
        { html: form_adddebt, type: "adddebt" },
        append_form,
    ) 
    $(".btn-addgoal").on(
        "click",
        { html: form_addgoal, type: "addgoal" },
        append_form,
    ) 
    $(".btn-addincome").on(
        "click",
        { html: form_addincome, type: "addincome" },
        append_form,
    ) 
});


function append_form(params) {
    ftype = params.data.type;
    $(".btn-add").attr("disabled", true);
    $(".tablecontainer").prepend(params.data.html);
    $(`.form-${ftype} #name`).focus();
    $(`.cancel-${ftype}`).on("click", function() {
        $(".btn-add").attr("disabled", false);
        $(`.form-${ftype}`).remove();
    });

}

let form_addspending = `
    <form class="form-add form-addspending" action="/addspending" method="POST">
        <div class="form-input-container">
            <label for="name">Name</label>
            <input type="text" id="name" name="name" placeholder="groceries" required>
        </div>
        <div class="form-input-container">
        <label for="amount">Amount</label>
        <input type="number" id="amount" name="amount" min="1" step="any" placeholder="64.65" required>
        </div>

        <div class="form-input-container">
            Optional
        </div>

        <div class="form-input-container">
        <label for="category">Category</label>
        <input type="text" id="category" name="category" placeholder="food (optional)">
        </div>
        <div class="form-input-container">
        <label for="owner">Owner</label>
        <input type="text" id="owner" name="owner" placeholder="John (optional)">
        </div>
        <div class="form-input-container">
        <label for="date">Date</label>
        <input type="date" id="date" name="date" placeholder="optional default is today's date">
        </div>
        <input class="submit-addspending" type="submit" value="Submit">
        <button class="cancel-addspending">Cancel</button>
    </form>
`

let form_addexpense = `
    <form class="form-add form-addexpense" action="/addexpense" method="POST">
        <div class="form-input-container">
            <label for="name">Name</label>
            <input type="text" id="name" name="name" placeholder="groceries" required>
        </div>
        <div class="form-input-container">
        <label for="amount">Amount</label>
        <input type="number" id="amount" name="amount" min="1" step="any" placeholder="64.65" required>
        </div>

        <div class="form-input-container">
            Optional
        </div>

        <div class="form-input-container">
        <label for="category">Category</label>
        <input type="text" id="category" name="category" placeholder="food (optional)">
        </div>
        <div class="form-input-container">
        <label for="owner">Owner</label>
        <input type="text" id="owner" name="owner" placeholder="John (optional)">
        </div>
        <div class="form-input-container">
        <label for="date">Date</label>
        <input type="date" id="date" name="date" placeholder="optional default is today's date">
        </div>
        <input class="submit-addexpense" type="submit" value="Submit">
        <button class="cancel-addexpense">Cancel</button>
    </form>
`

let form_addgoal = `
    <form class="form-add form-addgoal" action="/addgoal" method="POST">
        <div class="form-input-container">
            <label for="name">Name</label>
            <input type="text" id="name" name="name" placeholder="new bike" required>
        </div>
        <div class="form-input-container">
        <label for="target">Target Amount</label>
        <input type="number" id="target" name="target" min="1" step="any" placeholder="100" required>
        </div>
        <input type="hidden" id="amount" name="amount" min="1" step="any" value="0" required>

        <div class="form-input-container">
            Optional
        </div>
        <div class="form-input-container">
        <label for="owner">Owner</label>
        <input type="text" id="owner" name="owner" placeholder="John (optional)">
        </div>
        <div class="form-input-container">
        <label for="date">When do you goal it?</label>
        <input type="date" id="date" name="date">
        </div>
        <input class="submit-addgoal" type="submit" value="Submit">
        <button class="cancel-addgoal">Cancel</button>
    </form>
`
let form_adddebt = `
    <form class="form-add form-adddebt" action="/adddebt" method="POST">
        <div class="form-input-container">
            <label for="name">Name</label>
            <input type="text" id="name" name="name" placeholder="School loans" required>
        </div>
        <div class="form-input-container">
        <label for="amount">Amount</label>
        <input type="number" id="amount" name="amount" min="1" step="any" placeholder="100" required>
        </div>

        <div class="form-input-container">
            Optional
        </div>
        <div class="form-input-container">
        <label for="owner">Owner</label>
        <input type="text" id="owner" name="owner" placeholder="John (optional)">
        </div>
        <div class="form-input-container">
        <label for="date">When do you goal it payed off?</label>
        <input type="date" id="date" name="date">
        </div>
        <input class="submit-adddebt" type="submit" value="Submit">
        <button class="cancel-adddebt">Cancel</button>
    </form>
`

let form_addincome = `
    <form class="form-add form-addincome" action="/addincome" method="POST">
        <div class="form-input-container">
            <label for="name">Name</label>
            <input type="text" id="name" name="name" placeholder="paycheck" required>
        </div>
        <div class="form-input-container">
        <label for="amount">How Much</label>
        <input type="number" id="amount" name="amount" min="1" step="any" placeholder="400" required>
        </div>
        <div class="form-input-container">
        <label for="type">What type of income is it</label>
        <input type="text" id="type" name="type" placeholder="Active / Passive">
        </div>

        <div class="form-input-container">
            Optional
        </div>
        <div class="form-input-container">
        <label for="category">Category</label>
        <input type="text" id="category" name="category" placeholder="food (optional)">
        </div>
        <div class="form-input-container">
        <label for="owner">Owner</label>
        <input type="text" id="owner" name="owner" placeholder="John (optional)">
        </div>
        <div class="form-input-container">
        <label for="date">Date</label>
        <input type="date" id="date" name="date">
        </div>
        <input class="submit-addincome" type="submit" value="Submit">
        <button class="cancel-addincome">Cancel</button>
    </form>
`