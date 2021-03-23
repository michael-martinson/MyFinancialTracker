
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
    $(".btn-import").on(
        "click",
        { html: form_import, type: "import" },
        append_form,
    )
});


function append_form(params) {
    console.log("appending a form")
    ftype = params.data.type;
    $(".btn-form").attr("disabled", true);
    $(".add-buttons").after(params.data.html);
    $(`.form-${ftype} #name`).focus();
    $(`.cancel-${ftype}`).on("click", function() {
        $(".btn-form").attr("disabled", false);
        $(`.form-${ftype}`).remove();
    });

}

let form_import = `
    <form class="form-add form-import" action="/importcsv" method="POST" enctype="multipart/form-data">
        <div class="form-input-container">
            <input type="file" id="csvfile" name="csvfile" required>
        </div>
        <div class="form-input-container csvtableselect">
            <select name="tablename" required>
                <option value="spending">Import Spending Data</option>
                <option value="expenses">Import Expense Data</option>
                <option value="goals">Import Goal Data</option>
                <option value="debt">Import Debt Data</option>
                <option value="income">Import Income Data</option>
            </select>
        </div>
        <div class="form-input-buttons">
        <input class="btn submit-import" type="submit" value="Submit">
        <button class="btn cancel-import">Cancel</button>
        </div>
    </form>
`

let form_addspending = `
    <form class="form-add form-addspending" action="/addspending" method="POST">
        <div class="form-input-container">
            <label for="name">Name</label>
            <input type="text" id="name" name="name" placeholder="groceries" required>
            <label for="amount">Amount</label>
            <input type="number" id="amount" name="amount" min="1" step="any" placeholder="64.65" required>
        </div>
        <div class="form-input-container">
            Optional
            <label for="linkedExpense">Linked Expense</label>
            <input type="text" id="linkedExpense" name="linkedExpense" placeholder="groceries (optional)">
            <label for="category">Category</label>
            <input type="text" id="category" name="category" placeholder="food (optional)">
            <label for="owner">Owner</label>
            <input type="text" id="owner" name="owner" placeholder="John (optional)">
            <label for="date">Date</label>
            <input type="date" id="date" name="date" placeholder="optional default is today's date">
        </div>
        <div class="form-input-buttons">
            <input class="btn submit-addspending" type="submit" value="Submit">
            <button class="btn cancel-addspending">Cancel</button>
        </div>
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
            <label for="category">Category</label>
            <input type="text" id="category" name="category" placeholder="food (optional)">
            <label for="owner">Owner</label>
            <input type="text" id="owner" name="owner" placeholder="John (optional)">
            <label for="date">Date</label>
            <input type="date" id="date" name="date" placeholder="optional default is today's date">
        </div>
        <div class="form-input-buttons">
        <input class="btn submit-addexpense" type="submit" value="Submit">
        <button class="btn cancel-addexpense">Cancel</button>
        </div>
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
            <label for="owner">Owner</label>
            <input type="text" id="owner" name="owner" placeholder="John (optional)">
            <label for="date">When do you goal it?</label>
            <input type="date" id="date" name="date">
        </div>
        <div class="form-input-buttons">
        <input class="btn submit-addgoal" type="submit" value="Submit">
        <button class="btn cancel-addgoal">Cancel</button>
        </div>
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
            <label for="owner">Owner</label>
            <input type="text" id="owner" name="owner" placeholder="John (optional)">
            <label for="date">When do you goal it payed off?</label>
            <input type="date" id="date" name="date">
        </div>
        <div class="form-input-buttons">
        <input class="btn submit-adddebt" type="submit" value="Submit">
        <button class="btn cancel-adddebt">Cancel</button>
        </div>
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
            <label for="category">Category</label>
            <input type="text" id="category" name="category" placeholder="food (optional)">
            <label for="owner">Owner</label>
            <input type="text" id="owner" name="owner" placeholder="John (optional)">
            <label for="date">Date</label>
            <input type="date" id="date" name="date">
        </div>
        <div class="form-input-buttons">
            <input class="btn submit-addincome" type="submit" value="Submit">
            <button class="btn cancel-addincome">Cancel</button>
        </div>
    </form>
`