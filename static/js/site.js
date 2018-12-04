/*global TimelineLite, Bounce, Power2*/

var visualizations, auth, game, refresher, tl = new TimelineLite();

tl.staggerFrom(".column", .3, {opacity: 0, ease: Power2.easeInOut}, .2);

$(document).ready(function () {
    $(".menu .account")
        .popup({
            on: "click",
            inline: true,
            hoverable: true,
            position: "bottom right",
            lastResort: "left center",  // TODO: Find a permanent solution instead of an ugly last resort
            delay: {
                show: 300,
                hide: 800
            }
        });
    game = new Game();
    visualizations = new Visualizations([game]);
    auth = new Auth("form#auth");
    refresher = new Refresher();
});

function Refresher() {
    var myself = this;

    this.refreshButton = $("#refresh");
    this.refreshIcon = this.refreshButton.children("i");
    this.refreshStatus = $("#refresh-status");

    this.tl = new TimelineLite();
    this.refreshable = true;

    this.refreshButton.click(function () {
        if (myself.refreshable) {
            myself.refresh();
        }
    });

    // Auto-refresh
    setInterval(function () {
        if (myself.refreshable && document.hasFocus()) {
            myself.refresh();
        }
    }, 6e4);

    myself.refresh(true)
}

Refresher.prototype.refresh = function (autoRetry) {
    var myself = this;

    Promise.all([visualizations.update(), game.refresh()]).then(function() {
        myself.refreshable = true;
        // Indicate success
        myself.setStatus("Refreshed at " + moment().format("LTS"));
        myself.tl.to(myself.refreshIcon, .75, {rotation:"+=360", ease:Power2.easeInOut});
    }, function() {
        myself.refreshable = false;
        if (autoRetry) {
            setTimeout(function () {
                myself.refresh(true);
            }, 2000);
        }
        // Indicate failure
        myself.setStatus("You are being ratelimited!", 3000);
        myself.tl.to(myself.refreshIcon, .75, {rotation:"+=180", ease:Bounce.easeOut})
            .to(myself.refreshIcon, .75, {rotation:"-=180", ease:Bounce.easeOut});
    });
};

Refresher.prototype.setStatus = function (message, duration) {
    var myself = this,
        oldStatus = this.refreshStatus.text();

    this.refreshStatus.text(message);

    if (duration !== undefined) {
        this.refreshable = false;
        setTimeout(function () {
            myself.refreshStatus.text(oldStatus);
            myself.refreshable = true;
        }, duration);
    }
};