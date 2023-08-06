import json
import datetime
import requests
try:
    JSONDecodeError = json.decoder.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError


def cc_ding_talk_webhook_message_is_str_valid(content):
    """
    非空字符串
    :param content: 字符串
    :return: 非空 - True，空 - False
    """
    if content and content.strip():
        return True
    else:
        return False


class CCDingTalkWebhookMessage(object):
    """
    钉钉群自定义机器人（每个机器人每分钟最多发送20条），支持文本（text）、连接（link）、markdown三种消息类型！
    """
    def __init__(self, webhook_url: str):
        """
        机器人初始化
        """
        super(CCDingTalkWebhookMessage, self).__init__()
        self.headers = {'Content-Type': 'application/json; charset=utf-8'}
        self.webhook = webhook_url
        self.__msg_ts = []

    def send_text(self, msg, is_at_all=False, at_mobiles=None, at_dingtalk_ids=None):
        """
        text类型
        :param msg: 消息内容
        :param is_at_all: @所有人时：true，否则为false（可选）
        :param at_mobiles: 被@人的手机号（可选）
        :param at_dingtalk_ids: 被@人的dingtalkId（可选）
        :return: 返回消息发送结果
        """
        data_at = dict()
        data = {"msgtype": "text", "at": data_at}
        if cc_ding_talk_webhook_message_is_str_valid(msg):
            data["text"] = {"content": msg}
        else:
            print("text类型，消息内容不能为空！")
            raise ValueError("text类型，消息内容不能为空！")

        if is_at_all:
            data_at["isAtAll"] = is_at_all

        if at_mobiles:
            at_mobiles = list(map(str, at_mobiles))
            data_at["atMobiles"] = at_mobiles

        if at_dingtalk_ids:
            at_dingtalk_ids = list(map(str, at_dingtalk_ids))
            data_at["atDingtalkIds"] = at_dingtalk_ids

        print('text类型：%s' % data)
        return self.post(data)

    def send_image(self, pic_url):
        """
        image类型（表情）
        :param pic_url: 图片表情链接
        :return: 返回消息发送结果
        """
        if cc_ding_talk_webhook_message_is_str_valid(pic_url):
            data = {
                "msgtype": "image",
                "image": {
                    "picURL": pic_url
                }
            }
            print('image类型：%s' % data)
            return self.post(data)
        else:
            print("image类型中图片链接不能为空！")
            raise ValueError("image类型中图片链接不能为空！")

    def send_link(self, title, text, message_url, pic_url=''):
        """
        link类型
        :param title: 消息标题
        :param text: 消息内容（如果太长自动省略显示）
        :param message_url: 点击消息触发的URL
        :param pic_url: 图片URL（可选）
        :return: 返回消息发送结果

        """
        if cc_ding_talk_webhook_message_is_str_valid(title) and cc_ding_talk_webhook_message_is_str_valid(text) and cc_ding_talk_webhook_message_is_str_valid(message_url):
            data = {
                    "msgtype": "link",
                    "link": {
                        "text": text,
                        "title": title,
                        "picUrl": pic_url,
                        "messageUrl": message_url
                    }
            }
            print('link类型：%s' % data)
            return self.post(data)
        else:
            print("link类型中消息标题或内容或链接不能为空！")
            raise ValueError("link类型中消息标题或内容或链接不能为空！")

    def send_markdown(self, title, text, is_at_all=False, at_mobiles=None, at_dingtalk_ids=None):
        """
        markdown类型
        :param title: 首屏会话透出的展示内容
        :param text: markdown格式的消息内容
        :param is_at_all: 被@人的手机号（在text内容里要有@手机号，可选）
        :param at_mobiles: @所有人时：true，否则为：false（可选）
        :param at_dingtalk_ids: 被@人的dingtalkId（可选）
        :return: 返回消息发送结果
        """
        if cc_ding_talk_webhook_message_is_str_valid(title) and cc_ding_talk_webhook_message_is_str_valid(text):
            data_at = dict()
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": text
                },
                "at": data_at
            }
            if is_at_all:
                data_at["isAtAll"] = is_at_all

            if at_mobiles:
                at_mobiles = list(map(str, at_mobiles))
                data_at["atMobiles"] = at_mobiles

            if at_dingtalk_ids:
                at_dingtalk_ids = list(map(str, at_dingtalk_ids))
                data_at["atDingtalkIds"] = at_dingtalk_ids

            print("markdown类型：%s" % data)
            return self.post(data)
        else:
            print("markdown类型中消息标题或内容不能为空！")
            raise ValueError("markdown类型中消息标题或内容不能为空！")

    def send_action_card(self, action_card):
        """
        ActionCard类型
        :param action_card: 整体跳转ActionCard类型实例或独立跳转ActionCard类型实例
        :return: 返回消息发送结果
        """
        if isinstance(action_card, CCDingTalkWebhookMessageActionCard):
            data = action_card.get_data()
            print("ActionCard类型：%s" % data)
            return self.post(data)
        else:
            print("ActionCard类型：传入的实例类型不正确！")
            raise TypeError("ActionCard类型：传入的实例类型不正确！")

    def send_feed_card(self, links):
        """
        FeedCard类型
        :param links: 信息集（FeedLink数组）
        :return: 返回消息发送结果
        """
        link_data_list = []
        for link in links:
            if isinstance(link, CCDingTalkWebhookMessageFeedLink) or isinstance(link, CCDingTalkWebhookMessageCardItem):
                link_data_list.append(link.get_data())
        if link_data_list:
            # 兼容：1、传入FeedLink或CardItem实例列表；2、传入数据字典列表；
            links = link_data_list
        data = {"msgtype": "feedCard", "feedCard": {"links": links}}
        print("FeedCard类型：%s" % data)
        return self.post(data)

    def __update_msg_ts(self):
        """
        记录消息时间
        """
        timestamp = datetime.datetime.now().timestamp()
        if len(self.__msg_ts) >= 20:  # 因为钉钉60秒只能发20条，记录20条的ts
            del self.__msg_ts[0]
        self.__msg_ts.append(timestamp)
        return

    def __punish_msg_ts(self):
        for _ in range(0, 20):
            self.__update_msg_ts()

    def able_to_post(self) -> bool:
        if len(self.__msg_ts) < 20:
            return True
        first_ts = self.__msg_ts[0]
        timestamp = datetime.datetime.now().timestamp()
        if timestamp - first_ts > 60:  # 因为钉钉60秒只能发20条，这里比对当前时间和前面20条的时间，如果大于60，允许发送
            return True
        return False

    def post(self, data) -> dict:
        """
        发送消息（内容UTF-8编码）
        :param data: 消息数据（字典）
        :return: {'errcode': xxx, 'errmsg': 'xxx', '其他正常字段': '其他正常值'}
        """
        if self.able_to_post() is False:
            print("消息发送失败, 大于 60 秒 20 次")
            return {'errcode': 429, 'errmsg': '消息发送失败, 大于 60 秒 20 次'}
        self.__update_msg_ts()

        post_data = json.dumps(data)
        try:
            response = requests.post(self.webhook, headers=self.headers, data=post_data)
        except requests.exceptions.HTTPError as exc:
            print("消息发送失败， HTTP error: %d, reason: %s" % (exc.response.status_code, exc.response.reason))
            raise
        except requests.exceptions.ConnectionError:
            print("消息发送失败，HTTP connection error!")
            raise
        except requests.exceptions.Timeout:
            print("消息发送失败，Timeout error!")
            raise
        except requests.exceptions.RequestException:
            print("消息发送失败, Request Exception!")
            raise
        else:
            try:
                result = response.json()
            except JSONDecodeError:
                print("服务器响应异常，状态码：%s，响应内容：%s" % (response.status_code, response.text))
                return {'errcode': 500, 'errmsg': '服务器响应异常'}
            else:
                if not isinstance(result, dict):
                    return {'errcode': 500, 'errmsg': 'dingtalk 请求返回不是 dict'}
                print('发送结果：%s' % result)
                err_code = result.get('errcode')
                if err_code:
                    error_data = {
                        "msgtype": "text",
                        "text": {
                            "content": "钉钉机器人消息发送失败，原因：%s" % result.get('errmsg')
                        },
                        "at": {"isAtAll": False}
                    }
                    print("消息发送失败，错误：%s" % error_data)
                    if err_code != 130101:
                        print("自动重试")
                        requests.post(self.webhook, headers=self.headers, data=json.dumps(error_data))
                    else:
                        self.__punish_msg_ts()
                        return {'errcode': 429, 'errmsg': '消息发送失败, 大于 60 秒 20 次'}
                return result


class CCDingTalkWebhookMessageActionCard(object):
    """
    ActionCard类型消息格式（整体跳转、独立跳转）
    """
    def __init__(self, title, text, btn_list, btn_orientation=0, hide_avatar=0):
        """
        ActionCard初始化
        :param title: 首屏会话透出的展示内容
        :param text: markdown格式的消息
        :param btn_list: 按钮列表：（1）按钮数量为1时，整体跳转ActionCard类型；（2）按钮数量大于1时，独立跳转ActionCard类型；
        :param btn_orientation: 0：按钮竖直排列，1：按钮横向排列（可选）
        :param hide_avatar: 0：正常发消息者头像，1：隐藏发消息者头像（可选）
        """
        super(CCDingTalkWebhookMessageActionCard, self).__init__()
        self.title = title
        self.text = text
        self.btn_orientation = btn_orientation
        self.hide_avatar = hide_avatar
        btn_valid_list = []
        for btn in btn_list:
            if isinstance(btn, CCDingTalkWebhookMessageCardItem):
                btn_valid_list.append(btn.get_data())
        self.btns = btn_valid_list

    def get_data(self):
        """
        获取ActionCard类型消息数据（字典）
        :return: 返回ActionCard数据
        """
        if cc_ding_talk_webhook_message_is_str_valid(self.title) and cc_ding_talk_webhook_message_is_str_valid(self.text) and len(self.btns):
            if len(self.btns) == 1:
                # 整体跳转ActionCard类型
                data = {
                        "msgtype": "actionCard",
                        "actionCard": {
                            "title": self.title,
                            "text": self.text,
                            "hideAvatar": self.hide_avatar,
                            "btnOrientation": self.btn_orientation,
                            "singleTitle": self.btns[0].get("title"),
                            "singleURL": self.btns[0].get("actionURL")
                        }
                }
                return data
            else:
                # 独立跳转ActionCard类型
                data = {
                    "msgtype": "actionCard",
                    "actionCard": {
                        "title": self.title,
                        "text": self.text,
                        "hideAvatar": self.hide_avatar,
                        "btnOrientation": self.btn_orientation,
                        "btns": self.btns
                    }
                }
                return data
        else:
            print("ActionCard类型，消息标题或内容或按钮数量不能为空！")
            raise ValueError("ActionCard类型，消息标题或内容或按钮数量不能为空！")


class CCDingTalkWebhookMessageFeedLink(object):
    """
    FeedCard类型单条消息格式
    """
    def __init__(self, title, message_url, pic_url):
        """
        初始化单条消息文本
        :param title: 单条消息文本
        :param message_url: 点击单条信息后触发的URL
        :param pic_url: 点击单条消息后面图片触发的URL
        """
        super(CCDingTalkWebhookMessageFeedLink, self).__init__()
        self.title = title
        self.message_url = message_url
        self.pic_url = pic_url

    def get_data(self):
        """
        获取FeedLink消息数据（字典）
        :return: 本FeedLink消息的数据
        """
        if cc_ding_talk_webhook_message_is_str_valid(self.title) and cc_ding_talk_webhook_message_is_str_valid(self.message_url) and cc_ding_talk_webhook_message_is_str_valid(self.pic_url):
            data = {
                    "title": self.title,
                    "messageURL": self.message_url,
                    "picURL": self.pic_url
            }
            return data
        else:
            print("FeedCard类型单条消息文本、消息链接、图片链接不能为空！")
            raise ValueError("FeedCard类型单条消息文本、消息链接、图片链接不能为空！")


class CCDingTalkWebhookMessageCardItem(object):
    """
    ActionCard和FeedCard消息类型中的子控件
    """

    def __init__(self, title, url, pic_url=None):
        """
        CardItem初始化
        @param title: 子控件名称
        @param url: 点击子控件时触发的URL
        @param pic_url: FeedCard的图片地址，ActionCard时不需要，故默认为None
        """
        super(CCDingTalkWebhookMessageCardItem, self).__init__()
        self.title = title
        self.url = url
        self.pic_url = pic_url

    def get_data(self):
        """
        获取CardItem子控件数据（字典）
        @return: 子控件的数据
        """
        if cc_ding_talk_webhook_message_is_str_valid(self.pic_url) and cc_ding_talk_webhook_message_is_str_valid(self.title) and cc_ding_talk_webhook_message_is_str_valid(self.url):
            # FeedCard类型
            data = {
                "title": self.title,
                "messageURL": self.url,
                "picURL": self.pic_url
            }
            return data
        elif cc_ding_talk_webhook_message_is_str_valid(self.title) and cc_ding_talk_webhook_message_is_str_valid(self.url):
            # ActionCard类型
            data = {
                "title": self.title,
                "actionURL": self.url
            }
            return data
        else:
            print("CardItem是ActionCard的子控件时，title、url不能为空；是FeedCard的子控件时，title、url、pic_url不能为空！")
            raise ValueError("CardItem是ActionCard的子控件时，title、url不能为空；是FeedCard的子控件时，title、url、pic_url不能为空！")


class CCDingTalkWebhookMessageQueue(object):

    def __init__(self, webhook_urls: list):
        self.__chat_bots = list()
        for webhook_url in webhook_urls:
            chat_bot = CCDingTalkWebhookMessage(webhook_url)
            self.__chat_bots.append(chat_bot)
        pass

    def add_message(self, msg: str, at_mobiles: list):
        if len(msg) == 0:
            return
        for chat_bot in self.__chat_bots:
            r = chat_bot.send_text(msg=msg, at_mobiles=at_mobiles)
            if r.get('errcode') != 429:
                # 非高频限制均视为发送成功，结束发送流程
                break
            # 其他情况切换备用机器人发送
        return


class CCDingTalkReply(object):

    @staticmethod
    def text_msg(content: str, at_mobiles: list = None) -> str:
        if content is None or len(content) == 0:
            return ""
        text_dict = {"content": content}
        at_dict = {}
        if at_mobiles is not None:
            at_dict = {
                "atMobiles": at_mobiles,
                "isAtAll": False
            }
        result_dict = {
            "msgtype": "text",
            "text": text_dict,
            "at": at_dict
        }
        result_str = json.dumps(result_dict)
        return result_str
