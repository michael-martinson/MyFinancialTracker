
$(document).ready(function () {
    $(".notify").on(
        "load",
        function() {
            $(this).fadeOut();
        }
    );
    $(".btn-addspending").on(
        "click", 
        { html: form_addspending, type: "addspending" },
        append_form,
    );
    $(".btn-addexpense").on(
        "click",
        { html: form_addexpense, type: "addexpense" },
        append_form,
    );
    $(".btn-adddebt").on(
        "click",
        { html: form_adddebt, type: "adddebt" },
        append_form,
    );
    $(".btn-addgoal").on(
        "click",
        { html: form_addgoal, type: "addgoal" },
        append_form,
    ); 
    $(".btn-addincome").on(
        "click",
        { html: form_addincome, type: "addincome" },
        append_form,
    ); 
    $(".btn-import").on(
        "click",
        { html: form_import, type: "import" },
        append_form,
    );
    $(".e-data").on(
        "contextmenu",
        row_rightclick_e
    );
    $(".tr-data").on(
        "contextmenu",
        row_rightclick
    );
    $(".tablenav").on(
        "click",
        setactivetable
    );
    $('.data-buttons__left').on(
        "click",
        function() {
            let url = window.location.href.split('/');
            let thedate = url.pop().split('-');
            if (!thedate[1]) {
                current_date = new Date();
            } else {
                current_date = new Date(thedate[0], thedate[1]-1, thedate[2]);
            }
            if (current_date.getMonth() === 0) {
                new_date = new Date(current_date.getFullYear()-1, 11, 1);
            } else {
                new_date = new Date(current_date.getFullYear(), current_date.getMonth()-1, 1);
            }
            window.location = `/my${document.querySelector('.tablename').innerHTML}/${new_date.getFullYear()}-${new_date.getMonth()+1}-${new_date.getDate()}`;
        }
    );
    $('.data-buttons__right').on(
        "click",
        function() {
            let url = window.location.href.split('/');
            let thedate = url.pop().split('-');
            if (!thedate[1]) {
                current_date = new Date()
            } else {
                current_date = new Date(thedate[0], thedate[1]-1, thedate[2]);
            }
            console.log(current_date);
            if (current_date.getMonth() === 11) {
                new_date = new Date(current_date.getFullYear()+1, 0, 1);
            } else {
                new_date = new Date(current_date.getFullYear(), current_date.getMonth()+1, 1);
            }
            window.location = `/my${document.querySelector('.tablename').innerHTML}/${new_date.getFullYear()}-${new_date.getMonth()+1}-${new_date.getDate()}`;
        }
    );
});

// Get and post request logic
const request = ( url, params = {}, method = 'GET' ) => {
    let options = {
        method
    };
    if ( 'GET' === method ) {
        url += '?' + ( new URLSearchParams( params ) ).toString();
    } else {
        options.body = JSON.stringify( params );
    }
    
    return fetch( url, options ).then( response => location.reload() );
};
const get = ( url, params ) => request( url, params, 'GET' );
const post = ( url, params ) => request( url, params, 'POST' );

function setactivetable(event) {
    console.log(event.target);
    event.target.classList.add("tablenav-active");
}

function row_rightclick(event) {
    event.preventDefault();
    let buttons = document.createElement('div')
    buttons.className = "rowedit-buttons"
    buttons.innerHTML = rowedit_buttons;
    buttons.style.position = "absolute";
    buttons.style.left = `${event.clientX}px`;
    buttons.style.top = `${event.clientY}px`;
    $('body').append(buttons);
    $(`.rowedit-buttons`).on(
        "mouseleave",
        function() {
            $(this).remove();
        }
    );
    let rid = event.target.parentElement.cells[0].innerHTML;
    // Delete the row
    let tablename = document.querySelector(".tablename").innerHTML;
    $(`.rowedit__deleterow`).on(
        "click",
        function() {
            post("/deleterow", { "rid": rid, "tablename": tablename});
            $('.rowedit-buttons').remove();
        }
    );
}

let rowedit_buttons = `
    <button class="btn btn-rowedit rowedit__deleterow">Delete Row</button>
`

function row_rightclick_e(event) {
    event.preventDefault();
    let buttons = document.createElement('div')
    buttons.className = "rowedit-buttons"
    buttons.innerHTML = rowedit_buttons_e;
    buttons.style.position = "absolute";
    buttons.style.left = `${event.clientX}px`;
    buttons.style.top = `${event.clientY}px`;
    $('body').append(buttons);
    $(`.rowedit-buttons`).on(
        "mouseleave",
        function() {
            $(this).remove();
        }
    );
    let rid = event.target.parentElement.cells[0].innerHTML;

    // Show spending
    $(".rowedit__spending").on(
        "click",
        function() {
            console.log("Hello there", rid);
            $(`.stc-${rid}`).css("display", "table-cell");
            $('.rowedit-buttons').remove();
        }
    );

    // Hide spending
    $(".rowedit__hide").on(
        "click",
        function() {
            $(`.stc-${rid}`).css("display", "none");
            $('.rowedit-buttons').remove();
        }
    );

    // Delete the row
    let tablename = document.querySelector(".tablename").innerHTML;
    if (!tablename) {
        tablename = "expenses";
    }
    $(`.rowedit__deleterow`).on(
        "click",
        function() {
            post("/deleterow", { "rid": rid, "tablename": tablename});
            $('.rowedit-buttons').remove();
        }
    );
}

let rowedit_buttons_e = `
    <button class="btn btn-rowedit rowedit__spending">Show Spending</button>
    <button class="btn btn-rowedit rowedit__hide">Hide Spending</button>
    <button class="btn btn-rowedit rowedit__deleterow">Delete Row</button>
`

function append_form(params) {
    console.log("appending a form")
    ftype = params.data.type;
    $(".btn-form").attr("disabled", true);
    $("body").append(params.data.html);
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
            <input type="text" id="name" name="name" placeholder="Costco" required>
            <label for="amount">Amount</label>
            <input type="number" id="amount" name="amount" min="1" step="any" placeholder="205.20" required>
        </div>
        <div class="form-input-container">
            Optional
            <label for="linkedExpense">Linked Expense</label>
            <input type="text" id="linkedExpense" name="linkedExpense" placeholder="Groceries">
            <label for="category">Category</label>
            <input type="text" id="category" name="category" placeholder="Food ">
            <label for="date">Date</label>
            <input type="date" id="date" name="date">
            <label for="owner">Owner</label>
            <input type="text" id="owner" name="owner" placeholder="John">
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
            <input type="text" id="name" name="name" placeholder="rent" required>
            <label for="expected">Expected</label>
            <input type="number" id="expected" name="expected" min="1" step="any" placeholder="1000" required>
        </div>
        <div class="form-input-container">
            Optional
            <label for="repeat">Repeats</label>
            <select id="repeat" name="repeat" required>
                <option value="onetime">One time</option>
                <option value="weekly">Weekly</option>
                <option value="biweekly">Biweekly</option>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
            </select>
            <label for="date">Due Date</label>
            <input type="date" id="date" name="date">
            <label for="owner">Owner</label>
            <input type="text" id="owner" name="owner" placeholder="John">
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
            <label for="target">Target Amount</label>
            <input type="number" id="target" name="target" min="1" step="any" placeholder="100" required>
        </div>
        <input type="hidden" id="amount" name="amount" min="1" step="any" value="0" required>

        <div class="form-input-container">
            Optional
            <label for="date">When do you goal it?</label>
            <input type="date" id="date" name="date">
            <label for="owner">Owner</label>
            <input type="text" id="owner" name="owner" placeholder="John">
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
            <input type="text" id="name" name="name" placeholder="Student Loans" required>
            <label for="amount">Amount</label>
            <input type="number" id="amount" name="amount" min="1" step="any" placeholder="10000" required>
        </div>
        <div class="form-input-container">
            Optional
            <label for="date">When do you goal it payed off?</label>
            <input type="date" id="date" name="date">
            <label for="owner">Owner</label>
            <input type="text" id="owner" name="owner" placeholder="John">
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
            <label for="amount">How Much</label>
            <input type="number" id="amount" name="amount" min="1" step="any" placeholder="400" required>
            <label for="type">What type of income is it</label>
            <input type="text" id="type" name="type" placeholder="Active / Passive">
        </div>

        <div class="form-input-container">
            Optional
            <label for="category">Category</label>
            <input type="text" id="category" name="category" placeholder="">
            <label for="date">Date</label>
            <input type="date" id="date" name="date">
            <label for="owner">Owner</label>
            <input type="text" id="owner" name="owner" placeholder="John">
        </div>
        <div class="form-input-buttons">
            <input class="btn submit-addincome" type="submit" value="Submit">
            <button class="btn cancel-addincome">Cancel</button>
        </div>
    </form>
`