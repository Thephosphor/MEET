var personArray = new Array;
    		var CurPersonNum = 0;
    		// animate
    		var _in = ['bounceIn','bounceInDown','bounceInLeft','bounceInRight','bounceInUp','fadeIn','fadeInDown','fadeInDownBig','fadeInLeft','fadeInLeftBig','fadeInRight','fadeInRightBig','fadeInUp','fadeInUpBig','rotateIn','rotateInDownLeft','rotateInDownRight','rotateInUpLeft','rotateInUpRight','slideInDown','slideInLeft','slideInRight'];
    		var _out = ['bounceOut','bounceOutDown','bounceOutLeft','bounceOutRight','bounceOutUp','fadeOut','fadeOutDown','fadeOutDownBig','fadeOutLeft','fadeOutLeftBig','fadeOutRight','fadeOutRightBig','fadeOutUp','fadeOutUpBig','rotateOut','rotateOutDownLeft','rotateOutDownRight','rotateOutUpLeft','rotateOutUpRight','slideOutDown','slideOutLeft','slideOutRight'];

    		// 模拟推送数据
			var s = setInterval(function(){
				// get animate
				var rand_in = parseInt(Math.random() * _in.length,10);
    			var rand_out = parseInt(Math.random() * _out.length,10);
				if(CurPersonNum >= personArray.length){
					CurPersonNum = 0;
				}
				$('.show_info').show();
				$('.show_info').addClass(_in[rand_in]);
				setTimeout(function(){
					$('.show_info').removeClass(_in[rand_in]);
					// 更改展示的图片
					// var img = document.getElementsByClassName('element')[CurPersonNum].getElementsByTagName('img')[0];
					// img.setAttribute('src','img/b.png');
					++CurPersonNum;
					setTimeout(function(){
						$('.show_info').addClass(_out[rand_out]);
						setTimeout(function(){
							$('.show_info').removeClass(_out[rand_out]);
							$('.show_info').hide();
						},1000);
					},1500);
				},1000);
			},4500);

// 			// 生成虚拟数据
var style=$('style').val()
var l=$('len').val()
	        for(var i=0;i<10;i++){
				personArray.push({
		            image: "img/"+"a"+".png"
		        });
	        }

	        var table = new Array;
		    for (var i = 0; i < personArray.length; i++) {
		        table[i] = new Object();
		        if (i < personArray.length) {
		            table[i] = personArray[i];
		            table[i].src = personArray[i].thumb_image;
		        }
		        table[i].p_x = i % 20 + 1;
		        table[i].p_y = Math.floor(i / 20) + 1;
		    }


			var camera, scene, renderer;
			var controls;

			var objects = [];
			var targets = { table: [], sphere: [], helix: [], grid: [] };

			init();
			animate();

			function init() {

				camera = new THREE.PerspectiveCamera( 40, window.innerWidth / window.innerHeight, 1, 10000 );
				camera.position.z = 3000;

				scene = new THREE.Scene();

				// table

				for ( var i = 0; i < table.length; i ++ ) {

					var element = document.createElement( 'div' );
					element.className = 'element'+i;
					element.style.backgroundColor = 'rgba(0,127,127,' + ( Math.random() * 0.5 + 0.25 ) + ')';

					var aaaa = document.createElement('a');
					var img = document.createElement('img');
					img.src = table[ i ].image;
					aaaa.target = "_blank"
					aaaa.href = 'www.vfvf'+i+'.com1'
					aaaa.appendChild(img)
					element.appendChild(aaaa);


					var object = new THREE.CSS3DObject( element );
					object.position.x = Math.random() * 4000 - 2000;
					object.position.y = Math.random() * 4000 - 2000;
					object.position.z = Math.random() * 4000 - 2000;
					scene.add( object );

					objects.push( object );

					// 表格需要坐标进行排序的
					var object = new THREE.Object3D();
					// object.position.x = ( table[ i + 3 ] * 140 ) - 1330;
					// object.position.y = - ( table[ i + 4 ] * 180 ) + 990;
					object.position.x = ( table[ i ].p_x * 140 ) - 1330;
					object.position.y = - ( table[ i ].p_y * 180 ) + 990;

					targets.table.push( object );

				}

				// sphere

				var vector = new THREE.Vector3();
				var spherical = new THREE.Spherical();

				for ( var i = 0, l = objects.length; i < l; i ++ ) {

					var phi = Math.acos( -1 + ( 2 * i ) / l );
					var theta = Math.sqrt( l * Math.PI ) * phi;

					var object = new THREE.Object3D();

					spherical.set( 800, phi, theta );

					object.position.setFromSpherical( spherical );

					vector.copy( object.position ).multiplyScalar( 2 );

					object.lookAt( vector );

					targets.sphere.push( object );

				}

				// helix

				var vector = new THREE.Vector3();
				var cylindrical = new THREE.Cylindrical();

				for ( var i = 0, l = objects.length; i < l; i ++ ) {

					var theta = i * 0.175 + Math.PI;
					var y = - ( i * 5 ) + 450;

					var object = new THREE.Object3D();

					// 参数一 圈的大小 参数二 左右间距 参数三 上下间距
					cylindrical.set( 900, theta, y );

					object.position.setFromCylindrical( cylindrical );

					vector.x = object.position.x * 2;
					vector.y = object.position.y;
					vector.z = object.position.z * 2;

					object.lookAt( vector );

					targets.helix.push( object );

				}

				// grid

				for ( var i = 0; i < objects.length; i ++ ) {

					var object = new THREE.Object3D();

					object.position.x = ( ( i % 5 ) * 400 ) - 800; // 400 图片的左右间距  800 x轴中心店
					object.position.y = ( - ( Math.floor( i / 5 ) % 5 ) * 300 ) + 500;  // 500 y轴中心店
					object.position.z = ( Math.floor( i / 25 ) ) * 200 - 800;// 300调整 片间距 800z轴中心店

					targets.grid.push( object );

				}

				//渲染
				renderer = new THREE.CSS3DRenderer();
				renderer.setSize( window.innerWidth, window.innerHeight );
				renderer.domElement.style.position = 'absolute';
				document.getElementById( 'container' ).appendChild( renderer.domElement );

				// 鼠标控制
				controls = new THREE.TrackballControls( camera, renderer.domElement );
				controls.rotateSpeed = 0.5;
				controls.minDistance = 500;
				controls.maxDistance = 6000;
				controls.addEventListener( 'change', render );

				// 自动更换
				var ini = 0;
				setInterval(function(){
					ini = ini >= 3 ? 0 : ini;
					++ini;
					switch(ini){
						case 1:
							transform( targets.sphere, 1000 );
						break;
						case 2:
							transform( targets.helix, 1000 );
						break;
						case 3:
							transform( targets.grid, 1000 );
						break;
					}
				},8000);

				var button = document.getElementById( 'table' );
				button.addEventListener( 'click', function ( event ) {
					transform( targets.table, 1000 );
				}, false );

				var button = document.getElementById( 'sphere' );
				button.addEventListener( 'click', function ( event ) {
					transform( targets.sphere, 2000 );
				}, false );

				var button = document.getElementById( 'helix' );
				button.addEventListener( 'click', function ( event ) {
					transform( targets.helix, 2000 );
				}, false );

				var button = document.getElementById( 'grid' );
				button.addEventListener( 'click', function ( event ) {
					transform( targets.grid, 2000 );
				}, false );

				transform( targets.table, 2000 );

				//

				window.addEventListener( 'resize', onWindowResize, false );

			}

			function transform( targets, duration ) {

				TWEEN.removeAll();

				for ( var i = 0; i < objects.length; i ++ ) {

					var object = objects[ i ];
					var target = targets[ i ];

					new TWEEN.Tween( object.position )
						.to( { x: target.position.x, y: target.position.y, z: target.position.z }, Math.random() * duration + duration )
						.easing( TWEEN.Easing.Exponential.InOut )
						.start();

					new TWEEN.Tween( object.rotation )
						.to( { x: target.rotation.x, y: target.rotation.y, z: target.rotation.z }, Math.random() * duration + duration )
						.easing( TWEEN.Easing.Exponential.InOut )
						.start();

				}

				new TWEEN.Tween( this )
					.to( {}, duration * 2 )
					.onUpdate( render )
					.start();

			}

			function onWindowResize() {

				camera.aspect = window.innerWidth / window.innerHeight;
				camera.updateProjectionMatrix();

				renderer.setSize( window.innerWidth, window.innerHeight );

				render();

			}

			function animate() {

				// 让场景通过x轴或者y轴旋转  & z
				// scene.rotation.x += 0.011;
				scene.rotation.y += 0.002;

				requestAnimationFrame( animate );

				TWEEN.update();

				controls.update();

				// 渲染循环
				render();

			}

			function render() {

				renderer.render( scene, camera );

			}

