(function() {
    const lyricsBoxes = document.querySelectorAll('div.lyrics');
    if (lyricsBoxes.length < 1) return;

    // Create a grid
    function createGrid(className, hidden, innerHTML) {
        const grid = document.createElement('span');
        grid.className = className;
        if (hidden) grid.style.display = 'none';
        // Keep an empty span if there are no more lines
        grid.innerHTML = innerHTML;
        return grid;
    };

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

    // Should trigger Toggle if it's used but already been loaded
    var useToggle = false;

    for (var indexLyricBox = 0; indexLyricBox < lyricsBoxes.length; indexLyricBox++) {
        const lyricsBox = lyricsBoxes[indexLyricBox];

        const columns = Array.from(lyricsBox.querySelectorAll('.lyrics > div'));
        // Collect data, header, className and splitted lyrics
        const datas = columns.map(function (column) {
            const headerElement = column.firstElementChild;
            return {
                className: column.className.replace('row', ''),
                hidden: column.style.display === 'none',
                header: headerElement.innerHTML,
                headerClassName: headerElement.className,
                lyrics: processLyricsText(column.lastElementChild.querySelector('p').innerHTML)
            };
        });
        // Used when more than two columns
        useToggle = useToggle || datas.length > 2;
        // Find out maxnum of lyrics line count
        const lines = datas.reduce(function (prev, data) { return Math.max(prev, data.lyrics.length); }, 0);
        const gridTemplateColumns = lyricsBox.style.gridTemplateColumns;
        const contents = [];
        // Generate rows
        for (var line = 0; line < lines; line++) {
            contents.push(createRow('', gridTemplateColumns, datas.map(function (data) {
                // Keep an empty span if there are no more lines
                return createGrid(data.className, data.hidden, data.lyrics.length < lines ? '' : data.lyrics[line]);
            })));
        }
        // Clear
        lyricsBox.innerHTML = '';
        lyricsBox.style.cssText = '';
        lyricsBox.append(createRow('lyrics-header', gridTemplateColumns, datas.map(function (data) {
            return createGrid(data.headerClassName + ' ' + data.className, data.hidden, data.header);
        })));
        lyricsBox.append(createLyricsBox(contents));
    }

    if (useToggle) {
        // Triggers Toggle again
        const gadgetToggle = mw.loader.moduleRegistry['ext.gadget.toggle'];
        if (gadgetToggle && gadgetToggle.state === 'ready') {
            // Remove togglers
            while (document.querySelector('a.toggler-link')) {
                const toggler = document.querySelector('a.toggler-link');
                toggler.parentElement.insertBefore(toggler.firstChild, toggler);
                toggler.remove();
            }
            $(gadgetToggle.script);
        }
    }
})();