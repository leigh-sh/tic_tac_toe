// on DOM ready
document.addEventListener('DOMContentLoaded', function(event) {
    // Select all table cells and attach listeners to cells
    document.querySelectorAll('.cell').forEach( (cell) => {
        // Add click event listener to a cell
        cell.addEventListener('click', function (event) {
            var csrf = document.querySelector('input[type="hidden"]');
            console.log(`you have just clicked on cell ${this.dataset.row} / ${this.dataset.col}` );

            var data = new FormData();
            data.append('col', this.dataset.col);
            data.append('row', this.dataset.row);
            data.append('csrfmiddlewaretoken', csrf.value);

            var xhr = new XMLHttpRequest();
            xhr.open('POST', '/move/', true);
            xhr.onload = function () {
                // parse response as JSON
                data = JSON.parse(this.responseText);
                if (data.success === false) {
                    alert(data.message);
                    return;
                }
                // clear UI board and redraw with resposne data
                boardReDraw(data.board);
                if (data.is_over) {
                    document.getElementById('message').innerText = `We got a winner! Congratulations ${data.player}`;
                } else if (data.is_tie) {
                    document.getElementById('message').innerText = 'It\'s a tie!';
                }
            };
            xhr.send(data);
        })
    });

/*
    // add event listener to create clear game button
    document.getElementById('clearBoard').addEventListener('click', function (event) {
        xmlhttp=new XMLHttpRequest();
        xmlhttp.onreadystatechange = function() {
            if (xmlhttp.readyState==4 && xmlhttp.status==200) {
                // refresh page
                location.reload();
            }
        }
        xmlhttp.open("GET","/clear",true);
        xmlhttp.send();
    });
*/
});

function boardReDraw(board) {
    // clear board
    let cells = document.querySelectorAll('.cell')
    cells.forEach( (cell) => {
        cell.innerText = '';
    })

    // redraw board
    let idx = 0;
    cells.forEach( (cell) => {
        cell.innerText = board[idx++];
    });
    console.log(board);
}