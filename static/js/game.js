/*global TimelineLite, Bounce*/
function Game() {
    this.leaderboard = $("table#leaderboard");
    this.history = $("table#history");
    this.tl = new TimelineLite();

    var myself = this;

    $("button[name=guess]").click(function (e) {
        e.preventDefault();
        var guess = $(this).val();

        myself.saveGuess(guess);
    })
}

Game.prototype.refresh = function () {
    var myself = this,
        successCallback = function (data) {
            // Update history
            var body = myself.history.children("tbody"),
                guess = {
                    "1": ["trending_up", "Guessed the next earthquake would be higher"],
                    "-1": ["trending_down", "Guessed the next earthquake would be lower"]
                },
                correct = {
                    "1": ["check", "Correct"],
                    "0": ["clear", "Incorrect"],
                    "null": ["remove", "Waiting for the next earthquake"]
                };
            body.html("");
            data.history.slice(0, 5).forEach(function (quake) {
                var result = myself.iconfy(guess, quake.guess) + myself.iconfy(correct, quake.correct),
                    row = [quake.name, moment(quake.timestamp).format('YYYY-MM-DD [at] h:mm:ss A'), result];
                body.append(myself.rowify(row));
            });
            // Update score
            var score = data.history.filter(function (game) {
                return game.correct === 1;
            }).length;
            $("#game-score .detail").text(score);
            // Update leaderboard
            body = myself.leaderboard.children("tbody");
            body.html("");
            data.leaderboard.forEach(function (player) {
                var row = [player.username, player.score];
                body.append(myself.rowify(row));
            });
        };
    return $.get("./game").done(successCallback);
};

Game.prototype.saveGuess = function (guess) {
    var myself = this,
        successCallback = function () {
            myself.refresh();
        },
        failureCallback = function () {
            myself.tl.to(".account .material-icons", 1, {rotation: "+=360", ease: Bounce.easeOut})
        };
    $.post("/game", {"guess": guess}).done(successCallback).fail(failureCallback);
};

Game.prototype.iconfy = function (data, selector) {
    return "<i class='material-icons' title='" + data[selector][1] +"'>" + data[selector][0] + "</i>";
};

Game.prototype.rowify = function (items) {
    return "<tr>" + items.map(function (item) {
        return "<td>" + item + "</td>";
    }).reduce(function (a, b) {
        return a + b;
    }) + "</tr>";
};