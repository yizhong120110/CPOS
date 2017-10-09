$(document).ready(function() {

    $(document).keydown(function(event) {
        if (!( String.fromCharCode(event.which).toLowerCase() == 'f' && event.ctrlKey)) return true;
        event.preventDefault();
        var range = window.getSelection().getRangeAt(0);
        var column = $(range.commonAncestorContainer).parents('.mergely-column');
        handleFind(column);
        return false;
    });

    // find
    var find = $('.find');
    var flhs = find.clone().attr('id', 'mergely-editor-lhs-find');
    var frhs = find.clone().attr('id', 'mergely-editor-rhs-find');
    $('#mergely-editor-lhs').append(flhs);
    $('#mergely-editor-rhs').append(frhs);
    find.remove();
    
    function handleFind(column) {
        if (!column.length) {
            return false;
        }
        var ed = $('#mergely');
        var find = column.find('.find');
        var input = find.find('input[type="text"]');
        var side = column.attr('id').indexOf('-lhs') > 0 ? 'lhs' : 'rhs';
        var origautoupdate = ed.mergely('options').autoupdate;
        find.slideDown('fast', function() {
            input.focus();
            // disable autoupdate, clear both sides of diff
            ed.mergely('options', {autoupdate: false});
            ed.mergely('unmarkup');
        });
        find.find('.find-prev').click(function() {
            ed.mergely('search', side, input.val(), 'prev');
        });
        find.find('.find-next').click(function() {
            ed.mergely('search', side, input.val(), 'next');
        });
        find.find('.find-close').click(function() {
            find.css('display', 'none')
            ed.mergely('options', {autoupdate: origautoupdate});
        });
        
        input.keydown(function(evt) {
            if (evt.which != 13 && evt.which != 27) return true;
            if (evt.which == 27) {
                find.css('display', 'none');
                ed.mergely('options', {autoupdate: origautoupdate});
            }
            ed.mergely('search', side, input.val());
            return false;
        });
    }
});
