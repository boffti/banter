$.noConflict();
jQuery(function ($) {

    $("#changeDP").on('click', function () {
        $("#inputChangeDP").click();
    });

    $("input[name=dp]").on('change', function () {
        // alert(this.files[0].name);
        var fd = new FormData();
        var files = $('#inputChangeDP')[0].files;
        console.log(files);

        // Check file selected or not
        if (files.length > 0) {
            fd.append('file', files[0]);
            fd.append('_token', $('[name="csrf-token"]').attr('content'));

            $.ajax({
                url: '/update-dp',
                type: 'POST',
                data: fd,
                contentType: false,
                processData: false,
                success: function (response) {
                    if (response != '0') {
                        location.reload();
                        // alert(response);
                    } else {
                        alert('file not uploaded');
                    }
                },
            });
        } else {
            alert("Please select a file.");
        }
    });

    $('.grid').masonry({
        // options
        itemSelector: '.grid-item',
        // columnWidth: 50,
        // gutter: 8
    });

});