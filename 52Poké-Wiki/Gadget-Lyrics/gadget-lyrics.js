(function() {
    const lyricsBoxes = document.querySelectorAll('div.lyrics');
    if (lyricsBoxes.length < 1) return;

    // Create a row with grid layout
    function createRow(name, gridTemplateColumns, items) {
        const row = document.createElement('div');
        if (name) row.className = name;
        row.style.gridTemplateColumns = gridTemplateColumns;
        row.append.apply(row, items);
        return row;
    };

    function createLyricsBox(contents) {
        const box = document.createElement('div');
        box.className = 'roundy-6 bgwhite lyrics-content';
        box.append.apply(box, contents);
        return box
    };

    // Split by <br> and trim every line
    function processLyricsText(text) {
        return text.split(/<br\/?>/).map(function (line) { return line.trim(); });
    };

    for (var indexLyricBox = 0; indexLyricBox < lyricsBoxes.length; indexLyricBox++) {
        const lyricsBox = lyricsBoxes[indexLyricBox];

        const columns = Array.from(lyricsBox.querySelectorAll('.lyrics > div'));
        // Collect data, title, className and splitted lyrics
        const datas = columns.map(function (column) {
            return {
                title: column.firstElementChild.innerHTML,
                titleClassName: column.firstElementChild.className,
                lyrics: processLyricsText(column.lastElementChild.querySelector('p').innerHTML)
            };
        });
        // Find out maxnum of lyrics line count
        const lines = datas.reduce(function (prev, data) { return Math.max(prev, data.lyrics.length); }, 0);
        const gridTemplateColumns = lyricsBox.style.gridTemplateColumns;
        const contents = [];
        // Generate rows
        for (var line = 0; line < lines; line++) {
            contents.push(createRow('', gridTemplateColumns, datas.map(function (data) {
                const column = document.createElement('span');
                // Keep an empty span if there are no more lines
                column.innerHTML = data.lyrics.length < lines ? '' : data.lyrics[line];
                return column;
            })));
        }
        // Clear
        lyricsBox.innerHTML = '';
        lyricsBox.style.cssText = '';
        lyricsBox.append(createRow('lyrics-header', gridTemplateColumns, datas.map(function (data) {
            const header = document.createElement('span');
            header.className = data.titleClassName;
            header.innerHTML = data.title;
            return header;
        })));
        lyricsBox.append(createLyricsBox(contents));
    }
})();