//发送
$('.conLeft li').on('click',function(){
		$(this).addClass('bg').siblings().removeClass('bg');
		var intername=$(this).children('.liRight').children('.intername').text();
		$('.headName').text(intername);
		$('.newsList').html('');
	})

	//我方说话
	$('.sendBtn').on('click',function(){
		var news=$('#dope').val();
		// alert(news)
		if(news==''){
			alert('不能为空');
		}else{
			$('#dope').val('');
		var str='';
		str+='<li>'+
				'<div class="nesHead"><img src="../static/img/6.jpg"/></div>'+
				'<div class="news"><img class="jiao" src="../static/img/20170926103645_03_02.jpg">'+news+'</div>'+
			'</li>';
		// $('#dope').val('999')
		$('.newsList').append(str);
		$('.RightCont').scrollTop($('.RightCont')[0].scrollHeight );



		//发送消息对象
		var msg = new RongIMLib.TextMessage({content: news, extra: news});
		var conversationtype = RongIMLib.ConversationType.PRIVATE; // 单聊,其他会话选择相应的消息类型即可。
		var targetId = "2"; // 目标 Id
		RongIMClient.getInstance().sendMessage(conversationtype, targetId, msg, {
				onSuccess: function (message) {
					//message 为发送的消息对象并且包含服务器返回的消息唯一Id和发送消息时间戳
					console.log("Send successfully");
				},
				onError: function (errorCode, message) {
					var info = '';
					switch (errorCode) {
						case RongIMLib.ErrorCode.TIMEOUT:
							info = '超时';
							break;
						case RongIMLib.ErrorCode.UNKNOWN_ERROR:
							info = '未知错误';
							break;
						case RongIMLib.ErrorCode.REJECTED_BY_BLACKLIST:
							info = '在黑名单中，无法向对方发送消息';
							break;

						default :
							info = x;
							break;
					}
					console.log('发送失败:' + info);
				}
			}
		);

	}

})

//表情
	$('.ExP').on('mouseenter',function(){
		$('.emjon').show();
	})
	$('.emjon').on('mouseleave',function(){
		$('.emjon').hide();
	})
	$('.emjon li').on('click',function(){
		var imgSrc=$(this).children('img').attr('src');
		var str="";
		str+='<li>'+
				'<div class="nesHead"><img src="../static/img/6.jpg"/></div>'+
				'<div class="news"><img class="jiao" src="../static/img/20170926103645_03_02.jpg"><img class="Expr" src="'+imgSrc+'"></div>'+
			'</li>';
		$('.newsList').append(str);
		$('.emjon').hide();
		$('.RightCont').scrollTop($('.RightCont')[0].scrollHeight );
	})