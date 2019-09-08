var inP = $('.input-field');
console.log('inp的值', inP)
inP.on('blur', function () {
    if (!this.value) {
        $(this).parent('.f_row').removeClass('focus');
    } else {
        $(this).parent('.f_row').addClass('focus');
    }
}).on('focus', function () {
    $(this).parent('.f_row').addClass('focus');
    $('.btn').removeClass('active');
    $('.f_row').removeClass('shake');
});


$('.resetTag').click(function(e){
    e.preventDefault();
    $('.formBox').addClass('level-forget').removeClass('level-reg');
});

$('.back').click(function(e){
    e.preventDefault();
    $('.formBox').removeClass('level-forget').addClass('level-login');
});



$('.regTag').click(function(e){
    e.preventDefault();
    $('.formBox').removeClass('level-reg-revers');
    $('.formBox').toggleClass('level-login').toggleClass('level-reg');
    if(!$('.formBox').hasClass('level-reg')) {
        $('.formBox').addClass('level-reg-revers');
    }
});
$('.btn').each(function() {
     $(this).on('click', function(e){
         e.preventDefault();

        // var post_url = $(this).attr("action"); //get form action url
        // var request_method = $(this).attr("method"); //get form GET/POST method
        // var form_data = $(this).serialize(); //Encode form elements for submission
        //
        // $.ajax({
        //  url : post_url,
        //  type: request_method,
        //  async:false,
        //  data : form_data
        // }).done(function(response){
        // });
  //       $.ajax({
  //       url: "ajax_validate.php",
  //       type: 'POST',
  //       async:false,
  //       data: {host:host},
  //       dataType: 'json',
  //       success: function (data) {
  //         if (data.status == 'ok'){
  //         code = 1;
  //         }else if(data.status == 'error'){
  //         code = 0;
  //         }
  // });

        var finp =  $(this).parent('form').find('input');
        // 打印finp.html()的值
       console.log('finp.html()的值', finp.html());

        if (!finp.val() == 0) {
            // alert("用户名不能为空")
            // 打印finp.val()的值
            console.log('finp.val()的值', finp.val())
            $(this).addClass('active');

            var post_url = $(this).parent('form').attr("action"); //get form action url
            var request_method = $(this).parent('form').attr("method"); //get form GET/POST method
            var form_data = $(this).parent('form').serialize(); //Encode form elements for submission
            console.log('ajax', post_url, request_method, form_data)
            $.ajax({
             url : post_url,
             type: request_method,
             async:false,
             data : form_data,
             success: function () {
                console.log('ok')

                window.location.href='/topic'

             } })
            return false;

        }

        setTimeout(function () {

            inP.val('');

            $('.f_row').removeClass('shake focus');
            $('.btn').removeClass('active');


        }, 2000);
        // 打印inP.val()的值
        console.log('在if前inP.val()的值', inP.val())

        if(inP.val() == 0) {
            // 打印inP.val()的值
            console.log('在if后inP.val()的值', inP.val())
            inP.parent('.f_row').addClass('shake');

        }

        // inP.val('');
        // $('.f_row').removeClass('focus');




    });
});
