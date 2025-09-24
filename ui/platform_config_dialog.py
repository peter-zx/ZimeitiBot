{
"xiaohongshu": {
"name": "小红书",
"login_url": "https://creator.xiaohongshu.com/login",
"editor_url": "https://creator.xiaohongshu.com/publish?from=menu&target=image",
"steps": [
{"name": "打开发布入口", "action_type": "click_template", "template": "xiaohongshu/publish_entry.png"},
{"name": "选择上传图文", "action_type": "click_template", "template": "xiaohongshu/upload_image.png"},
{"name": "点击上传按钮", "action_type": "click_template", "template": "xiaohongshu/upload_image_button.png"},
{"name": "填写标题", "action_type": "type_template", "template": "xiaohongshu/title_input.png", "fill_from": "title"},
{"name": "填写正文", "action_type": "type_template", "template": "xiaohongshu/content_input.png", "fill_from": "content"},
{"name": "点击发布", "action_type": "click_template", "template": "xiaohongshu/publish_button.png"}
]
}
}