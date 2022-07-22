var dropdown='login';
function show_alert(text,type='error',close_delay=3000){
  types={
    'error':'.request-error-block',
    'success':'.request-success-block'
  }
  var block = $(types[type]);
  block.find('div').html(text);
  block.slideDown(100);
  setTimeout(function(){
      block.slideUp(100);
  }, close_delay);
}

function make_ajax_json(new_args){
  var margs={
    type:"POST",
    url:"",
    data:'',
    dataType:'json',
    final:function(){},
    success:function(){},
    error:function(){}
  };

  margs.success=function(data, textStatus, jqXHR){
    if(jqXHR.responseJSON){

      if(jqXHR.responseJSON['action']==='reload'){
        location.reload();
      }
      if(jqXHR.responseJSON['success']){
        show_alert(jqXHR.responseJSON['msg'],'success');
      }else{
        show_alert(jqXHR.responseJSON['msg'],'error');
      }
    }
    margs.final();
  };
  margs.error=function(jqXHR, textStatus, errorThrown) {
    if(jqXHR.responseJSON){
      if(jqXHR.responseJSON['action']==='reload'){
        location.reload();
      }
      show_alert(jqXHR.responseJSON['msg'],'error');
    }
    margs.final();
  };
  Object.keys(new_args).forEach(function(key) {
    margs[key] = new_args[key];
  });
  console.log("=>",margs);
  $.ajax(margs);
}
$(window).ready(function () {
  if(window.location.hash){
    var hash = window.location.hash.substring(1);
    console.log("HASH:",hash);
    if(hash=='login'){
      $('.auth-login-block.dropdown-content').css('display','block');
    }else if (hash=='register'){
      $('.auth-register-block.dropdown-content').css('display','block');
    }
  }
  $(document).click(function(e){
    var main_div = $(".auth-block");
    var divs = [$(".auth-"+dropdown+"-block")];
    for (var i = divs.length - 1; i >= 0; i--) {
      if (!main_div.is(e.target) && main_div.has(e.target).length === 0){
        divs[i].slideUp(200);
      }
    }
  });
  $('.auth-register-form input[type=submit').click(function(event){
    event.preventDefault();
    var this_button = $(this),
        this_form = $('.auth-register-form');

    this_button.attr("disabled", true);
    //console.log(this_form.serialize())
    make_ajax_json({
      url:urls.register,
      data: this_form.serialize(),
      final:function(){
        console.log("disable true");
        this_button.attr("disabled", false);
      },
      error:function(jqXHR, textStatus, errorThrown) {
        console.log(jqXHR.responseJSON)
        if(jqXHR.responseJSON['action'] === 'html'){
          $.each(jqXHR.responseJSON['response'], function(index, value) {
            if (index === "__all__") {
              console.log(value,value[0])
              this_form.find('.form-error.non-field-errors').html(value[0]);
            } else {
              console.log(index,value);
              this_form.find('.form-error[for=id_'+index+']').html(value[0]);
            }
          });
        }
        this.final();

      }
    });
  });
  $('form.auth-login-form input[type=submit').click(function(event){
    event.preventDefault();
    var this_button = $(this),
        this_form = $('.auth-login-form');

    this_button.attr("disabled", true);
    console.log(this_form.serialize());
    make_ajax_json({
      url:urls.login,
      data: this_form.serialize(),
      final:function(){
        console.log("disable true");
        this_button.attr("disabled", false);
      },
      error:function(jqXHR, textStatus, errorThrown) {
        console.log(jqXHR.responseJSON)
        if(jqXHR.responseJSON['action'] === 'html'){
          $.each(jqXHR.responseJSON['response'], function(index, value) {
            if (index === "__all__") {
              console.log(value,value[0]);
              this_form.find('.form-error.non-field-errors').html(value[0]);
            } else {
              console.log(index,value[0]);
              this_form.find('.form-error[for=id_'+index+']').html(value[0]);
            }
          });
        }
        this.final();
      }
    });
  });


  $('.auth-block').hover(function () {
    $('.auth-profile-block.dropdown-content').slideDown(200);
    $('.auth-'+dropdown+'-block.dropdown-content').slideDown(200);
  },function() {
    $('.auth-profile-block.dropdown-content').stop(true).delay(1000).slideUp(200);
  });

  $('.additional-input-link').click(function () {
    var el = $(this);
    if(el.attr('activity')==='close'){
      $('.additional-content-block.dropdown-content').slideUp(100);
      el.attr('activity','')
    }else{
      el.attr('activity','close');
      $('.additional-content-block.dropdown-content').slideDown(100);
    }

  });

  $('form#searchForm input.send-action').click(function(event){
    event.preventDefault();
    $(this).attr("disabled", true);
    console.log($('form#searchForm').serialize())
    make_ajax_json({
      url:urls.search,
      data: $('form#searchForm').serialize(),
      final:function(){
        console.log("disable true")
        $('form#searchForm input.send-action').attr("disabled", false);
      }
    });
  });

  $('form#downloadForm input.send-action').click(function(event){

    $.ajax({
        type: "POST",
        url:urls.download,
        data:$('form#downloadForm').serialize(),
        dataType:'json',
        success:function(data, textStatus, jqXHR) {
          console.log("data",jqXHR.responseJSON)
          if(jqXHR.responseJSON['success']){
            $('form#downloadForm').submit();
          }else{
            show_alert(data['msg'],'success');
          }
        },
        error:function(jqXHR, textStatus, errorThrown){show_alert(jqXHR.responseJSON['msg'],'error');}
    });
  });
  $('#register-button').click(function(){
    $('.auth-login-block.dropdown-content').css('display','none');
    $('.auth-register-block.dropdown-content').slideDown(200);
  });
});
