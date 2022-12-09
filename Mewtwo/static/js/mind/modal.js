const modal = `
<!-- login Modal start-->
<div class="modal fade" id="exampleModal"  aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">注册</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>

            <!--qr_login Modal start
            <div class="modal-body qr_login_group" style="height: 360px;">
                <img src="https://img0.baidu.com/it/u=3881180510,1470858589&fm=253&fmt=auto&app=138&f=JPEG?w=200&h=200" height="300px">
            </div>
            -->
            <!--qr_login Modal end-->

            <!--register Modal start-->
            <form>
                <div class="modal-body register_group" style="height: 360px;">
                    <h1 class="h3 mb-3 font-weight-normal">请输入用户名和密码</h1>
                    <label for="userName" class="sr-only"></label>
                    <input type="text" id="userName" class="form-control" placeholder="用户名" autocomplete="off" required autofocus>

                    <label for="inputPassword" class="sr-only"></label>
                    <input type="password" id="inputPassword" class="form-control" placeholder="密码" autocomplete="new-password" required>

                    <label for="inputPassword_" class="sr-only"></label>
                    <input type="password" id="inputPassword_" class="form-control" placeholder="密码" autocomplete="new-password" required>

                    <div style="margin-bottom: 10px; text-align:right;">
                        <button class="btn btn-sm btn-primary" type="submit" id="register_button">注册</button>
                    </div>
                </div>
            </form>
            <!--register Modal end-->

            <!--pw_login Modal start-->
            <form>
                <div class="modal-body pw_login_group" style="display: none;height: 360px;">
                    <h1 class="h3 mb-3 font-weight-normal">请输入用户名和密码</h1>
                    <label for="userName_login" class="sr-only">用户名</label>
                    <input type="text" id="userName_login" name="userName_login" class="form-control" placeholder="用户名" autocomplete="username" required autofocus>

                    <label for="inputPassword_login" class="sr-only">密码</label>
                    <input type="password" id="inputPassword_login" name="inputPassword_login" class="form-control" placeholder="密码" autocomplete="current-password" required>

                    <div style="margin-bottom: 10px; text-align:right;">
                        <button class="btn btn-sm btn-primary" id="login_button" type="button">登录</button>
                    </div>
                </div>
            </form>
            <!--pw_login Modal end-->

            <div class="modal-footer">
                <!--<a class="nav-link active" href="#" id="s_login_a">
                    <span data-feather="grid"></span>
                    扫码登录
                </a>-->
                <a class="nav-link active" id="register_a" href="#">
                    <span data-feather="check-circle"></span>
                    用户注册
                </a>
                <a class="nav-link active" href="#" id="p_login_a">
                    <span data-feather="smartphone"></span>
                    用户名登录
                </a>
            </div>
        </div>
    </div>
</div>
<!-- login Modal end-->

<!-- new  mind Modal start-->
<div class="modal fade" id="newMindModal"  aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">新建</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>

            <!--modal-body start-->
            <form>
                <div class="modal-body">
                    <label for="mindName" class="sr-only"></label>
                    <input type="text" id="mindName" class="form-control" placeholder="思维导图名称" autocomplete="off" required autofocus>
                    <div style="text-align:right;">
                        <button type="button" class="btn btn-info" id="new_mind_btn">确认创建</button>
                    </div>
                    <div class="form-group form-check">
                        <input type="checkbox" class="form-check-input" id="exampleCheck1">
                        <label class="form-check-label" for="exampleCheck1">新建后打开</label>
                     </div>
                </div>
            </form>
            <!--modal-body  end-->
        </div>
    </div>
</div>
<!-- new mind Modal end-->

<!-- share Modal start-->
<div class="modal fade" id="share_mind_modal"  aria-hidden="true">
    <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">分享成功</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>

            <!--modal-body start-->
            <div class="modal-body">请复制以下链接</div>
            <!--modal-body  end-->
        </div>
    </div>
</div>
<!-- share Modal end-->

`
$('body').append($(modal))