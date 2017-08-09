$(document).ready(function() {
    $(".btn-pref .btn").click(function () {
        $(".btn-pref .btn").removeClass("btn-primary").addClass("btn-default");
        // $(".tab").addClass("active"); // instead of this do the below
        $(this).removeClass("btn-default").addClass("btn-primary");
    });

    $.ajax({
        url: location.href,
        context: document.body,

        success: function(){
            var is_in_favourite = $("#add_to_favourites").attr("data-f");
            // console.log(is_in_favourite);
            if (is_in_favourite === "True") {
                // console.log("!");
                $("#add_to_favourites").hide();
            } else {
                $('#remove_from_favourites').hide();
            }

            var is_in_watch_list = $("#add_to_watch_list").attr("data-w");
            // console.log(is_in_watch_list);
            if (is_in_watch_list === "True") {
                // console.log("!!");
                $("#add_to_watch_list").hide();
            } else {
                $('#remove_from_watch_list').hide();
            }
        }
    });

    $('#likes').on('click', function(event){
        event.preventDefault();
        var element = $(this);

        $.ajax({
            url : '/like_movie/',
            type : 'POST',
            data : { movie_id : $(this).attr("data-id")},

            success : function(data){
                element.html(' ' + data);
            }
        });
    });

    $('#dislikes').on('click', function(event){
        event.preventDefault();
        var element = $(this);

        $.ajax({
            url : '/dislike_movie/',
            type : 'POST',
            data : { movie_id : $(this).attr("data-id")},

            success : function(data){
                element.html(' ' + data);
            }
        });
    });

    $('#add_to_favourites').on('click', function(event){
        event.preventDefault();

        $.ajax({
            url : '/add_to_favourites/',
            type : 'POST',
            data : { movie_id : $(this).attr("data-id")},

            success : function(){
                $('#add_to_favourites').hide();
                $('#remove_from_favourites').show();
            }
        });
    });

    $('#add_to_watch_list').on('click', function(event){
        event.preventDefault();

        $.ajax({
            url : '/add_to_watch_list/',
            type : 'POST',
            data : { movie_id : $(this).attr("data-id")},

            success : function(){
                $('#add_to_watch_list').hide();
                $('#remove_from_watch_list').show();
            }
        });
    });

    $('#remove_from_favourites').on('click', function(event){
        event.preventDefault();

        $.ajax({
            url : '/remove_from_favourites/',
            type : 'POST',
            data : { movie_id : $(this).attr("data-id")},

            success : function(){
                $('#add_to_favourites').show();
                $('#remove_from_favourites').hide();
            }
        });
    });

    $('#remove_from_watch_list').on('click', function(event){
        event.preventDefault();

        $.ajax({
            url : '/remove_from_watch_list/',
            type : 'POST',
            data : { movie_id : $(this).attr("data-id")},

            success : function(){
                $('#add_to_watch_list').show();
                $('#remove_from_watch_list').hide();
            }
        });
    });


    // You need these methods to add the CSRF token using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});