function Auth(formSelector) {
    this.form = $(formSelector);
    this.form.inputs = this.form.find("input");
    this.form.buttons = this.form.find("button");
    this.form.createAccountButton = this.form.find("button[value=create]");
    this.form.loginButton = this.form.find("button[value=login]");
    this.form.logoutButton = this.form.find("button[value=logout]");
    this.usernameDisplay = $("#username");
    this.statusMessage = $("#auth-status");
    this.secureStatus = $("#secure-status");

    var myself = this;

    this.form.submit(function (e) {
        e.preventDefault();
    });
    this.form.buttons.click(function (e) {
        e.preventDefault();
        var button = $(this),
            formData = myself.form.serializeArray(),
            payload = {};

        // Build the payload
        formData.forEach(function (input) {
            payload[input.name] = input.value;
        });
        payload.action = button.val();

        myself.submit(payload);
    });

    this.refresh();
}

Auth.prototype.refresh = function () {
    var myself = this,
        successCallback = function (data) {
            myself.setUser(data.username);
        };
    $.get("/user").done(successCallback);
    this.setSecureStatus(location.protocol === 'https:');
};

Auth.prototype.submit = function (payload) {
    var myself = this,
        successCallback = function () {
            myself.refresh();
            game.refresh();
        },
        failureCallback = function () {
            var action = payload.action;
            if (action === "create") {
                myself.setStatus("Failed to create account, username in use or password too short!")
            } else if (action === "login") {
                myself.setStatus("Failed to login, invalid username or password!")
            }
        };
    $.post("/user", payload).done(successCallback).fail(failureCallback);
};

Auth.prototype.setUser = function (username) {
    // This is merely aesthetic, you can't fake who you are
    var authorized = (username !== null);

    this.form.inputs.prop("disabled", authorized).val(username);
    this.form.createAccountButton.prop("disabled", authorized);
    this.form.loginButton.prop("disabled", authorized);
    this.form.logoutButton.prop("disabled", !authorized);
    this.usernameDisplay.text(username || "Not signed in");
    this.setStatus(authorized ? "Signed in" : "Please sign in or create an account");
};

Auth.prototype.setStatus = function (message) {
    this.statusMessage.text(message);
};

Auth.prototype.setSecureStatus = function (secure) {
    if (secure) {
        this.secureStatus.html("Secure<div class='detail'>Your connection is secure.</div>")
            .removeClass("red").addClass("green");
    } else {
        this.secureStatus.html("DANGER<div class='detail'>Your connection is not secure!</div>")
            .removeClass("green").addClass("red");
    }
};