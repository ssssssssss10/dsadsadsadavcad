from PyQt5.QtWidgets import QWidget, QLineEdit, QApplication, QLabel, \
    QPushButton
from PyQt5.QtCore import QSize, QByteArray, QUrl
from PyQt5.QtGui import QIcon, QPixmap, QFontMetrics, QDesktopServices
from PyQt5.QtCore import Qt as Fl
from PyQt5.Qt import pyqtSignal
import instaloader
import sys
import requests

no_photo = open("no_photo.jpg", "rb").read()


class MainWindow(QWidget):
    def __init__(self, *args, **kwars):
        super().__init__(*args, **kwars)

        # Sizes
        self.resize(200, 200)
        self.setMaximumSize(QSize(3272, 3402))
        self.setMinimumSize(326, 339)
        self.setWindowTitle("Inst")

        # Главное
        self.search_line = QLineEdit(self)
        self.search_line.editingFinished.connect(self.search_acc)
        self.mess_label = QLabel(self)
        self.mess_label.hide()
        self.mess_label.setText("Это приватный аккаунт")
        self.mess_label.resize(120, 40)
        self.mess_label.setAlignment(Fl.AlignHCenter | Fl.AlignTop)

        # 9 фото
        self.tables = 0
        self.right = QPushButton(self)
        self.right.setText("->")
        self.right.clicked.connect(self.next_table)
        self.right.hide()
        self.left = QPushButton(self)
        self.left.setText("<-")
        self.left.clicked.connect(self.prev_table)
        self.left.hide()
        self.pixmaps = []
        self.labels_px = []
        for i in range(3):
            mat = []
            mat2 = []
            for j in range(3):
                mat.append("")
                mat2.append(MLabel(self))
                mat2[j].clicked.connect(self.open_link)
                mat2[j].hide()
            self.pixmaps.append(mat)
            self.labels_px.append(mat2)
        flags = Fl.CustomizeWindowHint | Fl.WindowMinimizeButtonHint
        flags = flags | Fl.WindowFullScreen | Fl.WindowCloseButtonHint
        flags = flags | Fl.WindowMaximizeButtonHint
        self.setWindowFlags(flags)
        # Vars
        self.instloader_instance = instaloader.Instaloader()
        self.sh_profile = None
        self.show_profile = False
        self.search_lines = []
        self.loaded = 0
        for i in range(3):
            self.search_lines.append(SearchLine(self))
        self.init_ui()

    def resizeEvent(self, resize_event):
        self.init_ui()

    def init_ui(self):
        x_y = self.size()
        x = self.size().width()
        y = self.size().height()
        del x_y
        search_w = int(0.81595 * x)
        search_h = int(y * 0.0442)
        search_x = int(x * 0.0613)
        search_y = int(y * 0.00613)
        self.search_line.resize(search_w, search_h)

        b_suze = int(x * 0.09203) - 4
        self.right.resize(b_suze, search_h)
        self.right.move(x - b_suze - 2, search_y)
        self.left.resize(b_suze, search_h)
        self.left.move(2, search_y)
        search_x = 4 + b_suze
        self.search_line.move(search_x, search_y)
        for i in range(0, 3):
            self.search_lines[i].x = search_x
            self.search_lines[i].y = search_y + (i + 1) * search_h
            self.search_lines[i].width = search_w
            self.search_lines[i].height = search_h
            if self.search_lines[i].see:
                self.search_lines[i].generate()

        if self.show_profile:

            if self.sh_profile.inst_profile.is_private:
                self.mess_label.show()
            elif self.loaded == 0:
                self.mess_label.show()

            pic_size = int(0.3129 * min(x, y))
            b_x = int(x / 2 - 1.5 * pic_size)
            b_y = search_h + search_y + int(0.0184 * y)
            self.mess_label.move(int(x / 2) - 60, b_y + 5)
            tt = str(
                "Username: " + self.sh_profile.inst_profile.username)
            tt += "; ID: " + str(self.sh_profile.inst_profile.userid) + "; "
            tt += (
                " private " if self.sh_profile.inst_profile.is_private else "")
            tt += (
                " verified" if self.sh_profile.inst_profile.is_verified else "")
            tool_tip = tt + "\n" + "Подписчиков: " + str(
                self.sh_profile.inst_profile.followers) + "\nПодписок: "
            tool_tip += str(self.sh_profile.inst_profile.followees) +\
                "\nБиография:\n" + self.sh_profile.inst_profile.biography
            if self.sh_profile.inst_profile.biography == "":
                tool_tip = tool_tip[: -1]
            self.setToolTip(tool_tip)
            for i in range(3):
                for j in range(3):
                    if i * 3 + j >= self.loaded:
                        self.labels_px[i][j].hide()
                        continue

                    mn = min(self.pixmaps[i][j].size().width(),
                             self.pixmaps[i][j].size().height())
                    self.labels_px[i][j].resize(pic_size, pic_size)
                    self.labels_px[i][j].setPixmap(self.pixmaps[i][j].copy(
                        int(self.pixmaps[i][j].size().width() / 2) - int(
                            mn / 2),
                        int(self.pixmaps[i][j].size().height() / 2) - int(
                            mn / 2), mn, mn).scaled(pic_size, pic_size))
                    self.labels_px[i][j].move(b_x + pic_size * j,
                                              b_y + pic_size * i)
                    ind = i * 3 + j + self.tables * 9
                    sp = self.sh_profile.posts[ind].caption.split(".")
                    text = ""
                    opened = 0
                    for ii in sp:

                        if ii != "":
                            if opened > 0 and ii.count("”") > 0:
                                text = text[: -1]
                                opened -= 1
                            if ii.count("“") > 0:
                                if opened == 0:
                                    opened += ii.count("“") % 2

                            text += ii + ".\n"
                        else:
                            text += "."
                    if text[-1] == "\n":
                        text = text[: -1]
                    ur = self.labels_px[i][j].url.split()[1]
                    ur = ur[: len(ur) - 1]
                    text_tip = "Нравится: " + str(self.sh_profile.posts[
                                                      ind].likes) + \
                               "; Комментарии: " + str(
                        self.sh_profile.posts[
                            ind].comments) + "\nДата публикации: " + str(
                        self.sh_profile.posts[ind].date_local) \
                               + "\nНажмите, чтобы открыть в браузере /p/" + \
                               ur + "\nТекст публикации:\n" + text
                    self.labels_px[i][j].setToolTip(
                        text_tip[:len(text_tip) - 1])
                    self.labels_px[i][j].show()

        font = self.search_line.font()
        font.setPointSize(int(0.567 * int(y * 0.0442)))
        self.search_line.setFont(font)

    def open_link(self):
        ur = "https://instagram.com/p/" + self.sender().url.split()[1]
        ur = ur[:len(ur) - 1]
        print(ur)
        QDesktopServices.openUrl(QUrl(ur))

    def search_acc(self):
        t = self.search_line.text()
        if t == "":
            for i in range(3):
                self.search_lines[i].message = False
                self.search_lines[i].hide()
            return
        to_show = self.__search_acc__(t)
        for i in range(3):
            self.search_lines[i].message = False
            self.search_lines[i].hide()
        if len(to_show) == 0:
            self.search_lines[0].message = True
            self.search_lines[0].text = "Не найдено"
            self.search_lines[0].generate()
            self.search_lines[0].show()
        elif len(to_show) > 0:

            self.search_lines[0].new_profile(to_show[0])
            self.search_lines[0].generate()
            self.search_lines[0].show()
            if len(to_show) > 1:
                self.search_lines[1].new_profile(to_show[1])
                self.search_lines[1].generate()
                self.search_lines[1].show()

    def __search_acc__(self, text: str):
        result = []
        try:
            res = MProfile(instaloader.Profile.from_username(
                self.instloader_instance.context, text))
            if isinstance(res, MProfile):
                result.append(res)
        except instaloader.ProfileNotExistsException:
            pass
        except Exception as ex:
            pass

        try:
            res = MProfile(instaloader.Profile.from_id(
                self.instloader_instance.context, int(text)))
            if isinstance(res, MProfile):
                result.append(res)
        except instaloader.ProfileNotExistsException:
            pass
        except ValueError:
            pass
        except Exception as ex:
            pass
        return result

    def show_profile_f(self):
        self.mess_label.hide()

        for i in range(3):
            self.search_lines[i].message = False
            self.search_lines[i].hide()
        sender = self.sender()
        for i in range(3):
            if self.search_lines[i].label_for_text == sender or \
                    self.search_lines[i].label_for_pic == sender:
                self.sh_profile = self.search_lines[i].profile
                self.show_profile = True
                self.search_line.setText(self.sh_profile.inst_profile.username)
                break
        self.setWindowTitle(self.sh_profile.inst_profile.username)
        ico = QPixmap()
        ico.loadFromData(QByteArray(self.sh_profile.profile_pic))
        self.setWindowIcon(QIcon(ico))
        self.search_line.setText("")
        self.loaded = 0
        for i in self.sh_profile.inst_profile.get_posts():
            self.sh_profile.add_image(requests.get(i.url).content)
            self.sh_profile.add_post(i)
            self.loaded += 1
            if self.loaded == 10:
                break
        if self.loaded == 0:
            self.mess_label.setText("Публикаций пока нет")
            self.mess_label.show()
        if self.sh_profile.inst_profile.is_private:
            self.mess_label.setText("Это приватный аккаунт")
            self.mess_label.show()
        if self.loaded != 0 and not self.sh_profile.inst_profile.is_private:
            self.mess_label.hide()
        self.tables = 0

        if self.loaded > 9:
            self.right.show()
        self.set_table(0)
        self.init_ui()

    def set_table(self, ind):
        self.clear_table()
        ind *= 9
        for i in range(3):
            for j in range(3):
                if i * 3 + j + ind >= self.loaded:
                    return
                else:
                    self.pixmaps[i][j].loadFromData(
                        QByteArray(self.sh_profile.images[i * 3 + j + ind]))
                    self.labels_px[i][j].url = str(
                        self.sh_profile.posts[i * 3 + j + ind])

    def clear_table(self):
        for i in range(3):
            for j in range(3):
                self.pixmaps[i][j] = QPixmap()
                self.labels_px[i][j].setPixmap(QPixmap())
                self.labels_px[i][j].url = ""

    def next_table(self):

        self.tables += 1
        if self.tables >= 1:
            self.left.show()
        end = self.tables * 9 + 9
        ind = 0
        if self.loaded < end:
            for i in self.sh_profile.inst_profile.get_posts():
                if ind > self.loaded:
                    self.sh_profile.add_image(requests.get(i.url).content)
                    self.sh_profile.add_post(i)
                if ind >= end:
                    break
                ind += 1
            else:
                self.right.hide()
            self.loaded = end

        self.set_table(self.tables)
        self.init_ui()

    def prev_table(self):
        self.tables -= 1
        if self.tables == 0:
            self.left.hide()
        self.right.show()
        self.set_table(self.tables)
        self.init_ui()


class MProfile:
    def __init__(self, profile: instaloader.Profile):
        self.images = []
        self.inst_profile = profile
        self.posts = []
        if profile.profile_pic_url:
            self.profile_pic = requests.get(profile.profile_pic_url).content
            self.hasPic = True
        else:
            self.hasPic = False
            self.profile_pic = None

    def add_image(self, image):
        self.images.append(image)

    def add_post(self, post):
        self.posts.append(post)

    def __getitem__(self, item):
        return self.post[item]


class SearchLine:
    def __init__(self, parent):
        self.profile = None
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.label_for_text = ClickedLabel(parent)
        self.label_for_text.clicked.connect(parent.show_profile_f)
        self.label_for_text.setAlignment(Fl.AlignLeft | Fl.AlignVCenter)
        self.label_for_pic = ClickedLabel(parent)
        self.label_for_pic.clicked.connect(parent.show_profile_f)
        self.see = False
        self.message = False
        self.text = None
        self.hide()

    def new_profile(self, profile: MProfile):
        self.profile = profile

    def generate(self):
        size_pic = min(self.height, self.width)
        self.label_for_pic.resize(size_pic, size_pic)
        if not self.message:

            pxmap = QPixmap()
            if self.profile.hasPic:
                pxmap.loadFromData(QByteArray(self.profile.profile_pic))
            else:
                pxmap.loadFromData(no_photo)
            pxmap = pxmap.scaled(size_pic, size_pic)
            self.label_for_pic.setPixmap(pxmap)
            self.label_for_pic.move(self.x, self.y)
        else:
            self.label_for_pic.setPixmap(QPixmap())
        font = self.label_for_text.font()
        limit = int(self.height * 0.9)
        min_size_font = 0
        max_size_font = 200
        while max_size_font - min_size_font > 1:
            d = int((min_size_font + max_size_font) / 2)
            font.setPointSize(d)
            if QFontMetrics(font).height() > limit:
                max_size_font = d
            else:
                min_size_font = d
        font.setPointSize(min_size_font)
        self.label_for_text.setFont(font)

        self.label_for_text.resize(self.width - size_pic, self.height)
        if not self.message:
            self.label_for_text.move(self.x + size_pic + 10, self.y)
            text = self.profile.inst_profile.username
            if self.profile.inst_profile.is_private:
                text += " (private) "
            self.label_for_text.setText(text)
        else:
            self.label_for_text.move(self.x + 4, self.y)
            self.label_for_text.setText(self.text)

    def show(self):
        self.see = True
        self.label_for_text.show()
        self.label_for_pic.show()

    def hide(self):
        self.see = False
        self.label_for_pic.hide()
        self.label_for_text.hide()


class ClickedLabel(QLabel):
    clicked = pyqtSignal()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.clicked.emit()


class MLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, *args, **kwars):
        super().__init__(*args, **kwars)
        self.url = None

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.clicked.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()
    sys.exit(app.exec())
