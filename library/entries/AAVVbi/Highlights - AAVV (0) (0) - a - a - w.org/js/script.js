$(document).ready(function(){
	rozwinMenu();
	fitWindow();
	przypnijMenu();
	//icheckcall();
	checkedCheckbox();
	// Scroll the whole document
	$('#containerMENU').localScroll({
	   target:'body',
	   event:'click.localScroll',
	   offset: {
			top: -$('#containerMENU').height()-20,
			left: 0
		},
	});
        // [dwb] double call to sender.php
	// $('#register-form').ajaxForm();
	$('#register-form').submit(function() {
		$(this).ajaxSubmit({target:$('#register-form')});
		return false; 
	});
	setCommentSubmit();
	$('.comment-form textarea').each(function(){
		if($(this).html()==''){
			$(this).html('Comments (please be polite and try to be constructive)');
		}
	});
});
function setCommentSubmit(){
	$('.comment-form').submit(function() {
		$(this).ajaxSubmit({beforeSerialize: function($form, opts) { 
			if($form.find('textarea').html()=='Comments (please be polite and try to be constructive)'){
				$form.find('textarea').html('');
			}
		},beforeSubmit: function(arr,$form, opts) { 
			if($form.find('textarea').html()==''){
				$form.find('textarea').html('Comments (please be polite and try to be constructive)');
			}
			$form.find('.submit-check').css('opacity',1);
		},success:submitCheck});
		return false; 
	});
}
function submitCheck(resp,status,xhr,target){
	target.find('input[type=submit]').val('RESUBMIT');
	target.find('.submit-check').css('opacity',0);
	setCommentSubmit();
}

	
$(window).resize(function(){
	fitWindow();
	$('#containerMENU').unbind('click.localScroll');
	$('#containerMENU').localScroll({
	   target:'body',
	   event:'click.localScroll',
	   offset: {
			top: -$('#containerMENU').height()-20,
			left: 0
		},
	});
});		

$(window).scroll(function(){
	przypnijMenu();
});

/* icheck wywołanie
function icheckcall() {
	$('input').iCheck({
    checkboxClass: 'icheckbox_square-purple',
    radioClass: 'iradio_square-purple',
    increaseArea: '20%' // optional
  });
	$('#checkbox-student').on('ifChecked', function(event){
		
	});
}*/

function checkedCheckbox() {
	$('#checkbox-student').change(function(){
		if (this.checked) {			
			$('#label-fee-disabled').css('color', '#ffffff');
			$('#checkbox-fee').attr('disabled', false);
		}else {
			$('#label-fee-disabled').css('color', '#888888');
			$('#checkbox-fee').attr('disabled', true);
			$('#checkbox-fee').removeAttr('checked');
		}
	});
}

//dopasowanie okna - reposonsywnosc
function fitWindow(){
	var dpr = 1;
	//if(window.devicePixelRatio !== undefined) dpr = window.devicePixelRatio;
	dpr = Math.max(1,$(window).width()/screen.width);
	if(dpr>=2){
	   $('.state1').addClass('state4');
	   $('.state4').removeClass('state1');
	   $('body').css('font-size','30px');

	}else{
		if($(window).width()<500){
		   $('.state1').addClass('state3');
		   $('.state2').addClass('state3');
		   $('.state3').removeClass('state1');
		   $('.state3').removeClass('state2');
		}else if($(window).width()<1000){
		   $('.state1').addClass('state2');
		   $('.state3').addClass('state2');
		   $('.state2').removeClass('state1');
		   $('.state2').removeClass('state3');
		}else{
		   $('.state3').addClass('state1');
		   $('.state2').addClass('state1');
		   $('.state1').removeClass('state3');
		   $('.state1').removeClass('state2');
		}
	}	
}
var waiter;
var waitee;

$(window).ready(function() {
	fitWindow();
	$('#containerB').click(function(){
		if(!$('#containerB .hide-block').hasClass('hide-block-on')){
			$('#containerB .hide-block').switchClass('','hide-block-on',200);
		}else{
			$('#containerB .hide-block').switchClass('hide-block-on','',200);
		}
	});
	
	$('#containerF').click(function(){
		if(!$('#containerF .hide-block').hasClass('hide-block-on')){
			$('#containerF .hide-block').switchClass('','hide-block-on',200);
		}else{
			$('#containerF .hide-block').switchClass('hide-block-on','',200);
		}
	});
	
	$('#containerI').click(function(){
		if(!$('#containerI .hide-block').hasClass('hide-block-on')){
			$('#containerI .hide-block').switchClass('','hide-block-on',200);
		}else{
			$('#containerI .hide-block').switchClass('hide-block-on','',200);
		}
	});
	
	$('#containerC').click(function(){
		$('#containerC.state3 .main-text p').toggle(200);
		if(!$('#containerC.state3 .wrapper').hasClass('on')){
			$('#containerC.state3 .wrapper').addClass('on');
		}else{
			$('#containerC.state3 .wrapper').removeClass('on');
		}

		$('#containerC.state4 .main-text p').toggle(200);
		if(!$('#containerC.state4 .wrapper').hasClass('on')){
			$('#containerC.state4 .wrapper').addClass('on');
		}else{
			$('#containerC.state4 .wrapper').removeClass('on');
		}
	});
	$('#containerH .expander').click(function(){
		if($(this).hasClass('expanded')){
			$(this).removeClass('expanded');
			$(this).parent().removeClass('highlighted');
			$(this).parent().next().removeClass('highlighted');
			$(this).parent().next('.abstract').animate({height:0,paddingBottom:0},300);
		}else{
			$('#containerH .expander').each(function(){
				if($(this).hasClass('expanded')){
					$(this).removeClass('expanded');
					$(this).parent().removeClass('highlighted');
					$(this).parent().next().removeClass('highlighted');
					$(this).parent().next('.abstract').animate({height:0,paddingBottom:0},300);
				}
			});
			$(this).addClass('expanded');
			$(this).parent().addClass('highlighted');
			$(this).parent().next().addClass('highlighted');
			$(this).parent().next('.abstract').css('height','auto');
			$(this).parent().next('.abstract').css('opacity',0);
			waitee = $(this);
			waiter = setTimeout(waitForExpansion,10);
		}
	});
	$('#register').click(function(){
		$('#register_box').css('display','block');
	});
	$('#logged_name').click(function(){
		if($(this).hasClass('expanded')){
			$(this).removeClass('expanded');
			$('#unregister').css('display','none');
		}else{
			$(this).addClass('expanded');
			$('#unregister').css('display','inline');
		}
	});
	$('.x').click(function(){
		$(this).parent().css('display','none');
	});
	$('textarea').focus(function(){
		if($(this).html()=="Comments (please be polite and try to be constructive)"){
			$(this).html('');
			$(this).css('color','#000000');
		}
		$(this).animate({height:55});
	});
	$('textarea').blur(function(){
		if($(this).html()==""){
			$(this).html("Comments (please be polite and try to be constructive)");
			$(this).css('color','#9baaaa');
			$(this).animate({height:35});
		}
	});
});
function waitForExpansion(){	
	theight = waitee.parent().next('.abstract').height();
	waitee.parent().next('.abstract').css('height',0);
	waitee.parent().next('.abstract').css('opacity',1);
	waitee.parent().next('.abstract').animate({height:theight+10,paddingBottom:10},{duration:300,complete:function(){
		$(this).css('height','auto');
	}});
}


function przypnijMenu(){
	
	if($(window).scrollTop()<$('#containerB').offset().top-$('#containerMENU').height()){
		$('#containerMENU').addClass('notfixednow', 0, 'easeOutQuint');
		$('#menu-fixed-hack').height('0');
		
		
	}else{
		$('#containerMENU').removeClass('notfixednow', 0, 'easeOutQuint');
		var wysokoscMenu = $('#containerMENU').height();
		$('#menu-fixed-hack').height(wysokoscMenu+20);
	
	}
}

function rozwinMenu(){
	$('#containerMENU .menu-name').click(function(){
		$('.main-menu').toggleClass('main-menu-visible', 300, 'easeOutQuint');
		$('.menu-image').toggleClass('menu-image-visible', 300, 'easeOutQuint');
		$('.menu-name').toggleClass('hidden', 300, 'easeOutQuint');
	});
	$('#containerMENU .menu-image').click(function(){
		$('.main-menu').toggleClass('main-menu-visible', 300, 'easeOutQuint');
		$('.menu-name').toggleClass('hidden', 300, 'easeOutQuint');
		$('.menu-image').toggleClass('menu-image-visible', 300, 'easeOutQuint');
	});
	$('#containerMENU .main-menu li a').click(function(e){
		if($(this).data('eventPhase')==0){
			$(this).data('eventPhase',1);
		}else{
			e.stopImmediatePropagation();
			e.preventDefault();
			e.stopPropagation();
			$(this).data('eventPhase',0);
			var clickedElement=$(this);
			$('.main-menu').removeClass('main-menu-visible', 300, 'easeOutQuint');
			$('.menu-image').removeClass('menu-image-visible', 300, 'easeOutQuint');
			$('.menu-name').removeClass('hidden', 300, 'easeOutQuint',function(){clickedElement.trigger('click');});
			
		}
	});
}
