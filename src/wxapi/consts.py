#coding=utf-8

'''
常量；const：不要修改
最后一个 _GET 表示的请求方法，_GET 和  _POST
'''
class WXAPI(object):
    '''
    微信获取凭证URL
    '''
    ACCESS_TOKEN_GET = 'https://api.weixin.qq.com/cgi-bin/token'
    
    '''
    Oauth2认证，获取 code
    '''
    OAUTH2_AUTHORIZE = 'https://open.weixin.qq.com/connect/oauth2/authorize'
    
    '''
    Oauth2认证，获取 access_token
    '''
    OAUTH2_ACCESS_TOKEN = 'https://api.weixin.qq.com/sns/oauth2/access_token'
    
    '''
    Oauth2认证，获取 snsapi_userinfo
    '''
    OAUTH2_SNSAPI_USERINFO = 'https://api.weixin.qq.com/sns/userinfo'
    
    '''
    微信菜单添加 
    '''
    MENU_CREATE_POST = 'https://api.weixin.qq.com/cgi-bin/menu/create'
    
    '''
    微信菜单查看
    '''
    MENU_GET_GET = 'https://api.weixin.qq.com/cgi-bin/menu/get'
    
    '''
    微信菜单删除
    '''
    MENU_DELETE_GET = 'https://api.weixin.qq.com/cgi-bin/menu/delete'
    
    '''
    查询分组
    '''
    USER_GROUPS_GET = 'https://api.weixin.qq.com/cgi-bin/groups/get'
    
    '''
    获取用户基本信息
    '''
    USER_INFO_GET = 'https://api.weixin.qq.com/cgi-bin/user/info'
    
    '''
    获取关注者列表
    '''
    USER_LIST_GET = 'https://api.weixin.qq.com/cgi-bin/user/get'
    
    '''
    错误常量
    '''
    ERROR_INFO = {'-1':'系统繁忙',
                  '0':'请求成功',
                  '40001':'验证失败',
                  '40002':'不合法的凭证类型',
                  '40003':'不合法的OpenID',
                  '40004':'不合法的媒体文件类型',
                  '40005':'不合法的文件类型',
                  '40006':'不合法的文件大小',
                  '40007':'不合法的媒体文件id',
                  '40008':'不合法的消息类型',
                  '40009':'不合法的图片文件大小',
                  '40010':'不合法的语音文件大小',
                  '40011':'不合法的视频文件大小',
                  '40012':'不合法的缩略图文件大小',
                  '40013':'不合法的APPID',
                  '40014':'不合法的access_token',
                  '40014':'不合法的access_token',
                  '40015':'不合法的菜单类型',
                  '40016':'不合法的按钮个数',
                  '40017':'不合法的按钮个数',
                  '40018':'不合法的按钮名字长度',
                  '40019':'不合法的按钮KEY长度',
                  '40020':'不合法的按钮URL长度',
                  '40021':'不合法的菜单版本号',
                  '40022':'不合法的子菜单级数',
                  '40023':'不合法的子菜单按钮个数',
                  '40024':'不合法的子菜单按钮类型',
                  '40025':'不合法的子菜单按钮名字长度',
                  '40026':'不合法的子菜单按钮KEY长度',
                  '40027':'不合法的子菜单按钮URL长度',
                  '40028':'不合法的自定义菜单使用用户',
                  '40029':'不合法的oauth_code',
                  '40030':'不合法的refresh_token ',
                  '40031':'不合法的openid列表',
                  '40032':'不合法的openid列表长度',
                  '40033':'不合法的请求字符，不能包含\uxxxx格式的字符',
                  '40035':'不合法的参数',
                  '40038':'不合法的请求格式',
                  '40039':'不合法的URL长度 ',
                  '41001':'缺少access_token参数',
                  '41002':'缺少appid参数',
                  '41003':'缺少refresh_token参数',
                  '41004':'缺少secret参数',
                  '41005':'缺少多媒体文件数据',
                  '41006':'缺少media_id参数',
                  '41007':'缺少子菜单数据',
                  '42001':'access_token超时',
                  '43001':'需要GET请求',
                  '43002':'需要POST请求',
                  '43003':'需要HTTPS请求',
                  '44001':'多媒体文件为空',
                  '44002':'POST的数据包为空',
                  '44003':'图文消息内容为空',
                  '45001':'多媒体文件大小超过限制',
                  '45002':'消息内容超过限制',
                  '45003':'标题字段超过限制',
                  '45004':'描述字段超过限制',
                  '45005':'链接字段超过限制',
                  '45006':'图片链接字段超过限制',
                  '45007':'语音播放时间超过限制',
                  '45008':'图文消息超过限制',
                  '45009':'接口调用超过限制',
                  '45010':'创建菜单个数超过限制',
                  '46001':'不存在媒体数据',
                  '46002':'不存在的菜单版本',
                  '46003':'不存在的菜单数据',
                  '47001':'解析JSON/XML内容错误',
                  '48001':'api功能未授权，请确认公众号已获得该接口，可以在公众平台官网-开发者中心页中查看接口权限',
                  '50001':'用户未授权该api',
                  '61451':'参数错误(invalid parameter)',
                  '61452':'无效客服账号(invalid kf_account)',
                  '61453':'客服帐号已存在(kf_account exsited)',
                  '61454':'客服帐号名长度超过限制(仅允许10个英文字符，不包括@及@后的公众号的微信号)(invalid kf_acount length)',
                  '61455':'客服帐号名包含非法字符(仅允许英文+数字)(illegal character in kf_account)',
                  '61456':'客服帐号个数超过限制(10个客服账号)(kf_account count exceeded)',
                  '61457':'无效头像文件类型(invalid file type)',
                  '61450':'系统错误(system error)',
                  '61500':'日期格式错误',
                  '61501':'日期范围错误'
    }

'''
消息类型
DEFAULT ：系统内部消息形式：指定消息，
如果用户inputCode找不到对应的response，那么回复默认指定消息,inputCode='default'
'''
class MsgType:
    TEXT = 'text'
    IMAGE = 'image'
    VOICE = 'voice'
    VIDEO = 'video'
    MUSIC = 'music'
    LINK = 'link'
    LOCATION = 'location'
    EVENT = 'event'
    NEWS = 'news'
    CLICK = 'CLICK'
    VIEW = 'view'
    
    DEFAULT = 'default'
    
