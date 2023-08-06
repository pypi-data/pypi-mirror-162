from manim import *
from .emobjects import *
import json

WAITTIME = 1.5

class EScene(Scene):
    mobjs = {
            "logo" : Tex(r"$\vec{F}$", r"(m)", substrings_to_isolate="m"),
            "line" : Line(start=np.array([-8, -2.5, 0]), end=np.array([9, -2.5, 0]))
            }
    sub_id = 0
    subtitle = VGroup(Text(""), Text(""))

    subtitles = []

    conf = {}

    def init_files(self, file):
        conf = open(file.replace('lessons', 'configs').replace('py', 'json') , mode="rt", encoding='utf-8' )
        self.conf = json.load(conf)
        sLang = self.conf["init"]["lang"]
        sub_file = open(file.replace('lessons', f'subtitles/{sLang}').replace('py', 'txt'), mode="rt", encoding='utf-8' )
        self.subtitles = sub_file.readlines()

    def get_banner(self, mode):
        if mode == "y":
            rect = RoundedRectangle(corner_radius=0.23, height=1, width=1.41)
            rect.scale(4).set_fill("#DA271E", 1).set_stroke(width=0)
            tri = RoundedTriangle() 
            tri.stretch(factor=1.15, dim=1)
            tri.rotate(-PI/2).set_stroke(width=0)
            tri.set_fill(WHITE, 1).move_to(rect.get_center())
            you = Text("YouTube Edition", font="YouTube Sans", color=WHITE)         
            you.rescale_to_fit(rect.get_width()*0.9, 0).next_to(rect, DOWN)
            banner = VGroup(rect, tri, you)

        elif mode == "d":
            logo = Text("", font="Font Awesome").scale(7)
            textb = Text("Debug Mode", font="YouTube Sans", color=WHITE)         
            textb.rescale_to_fit(logo.get_width()*0.9, 0).next_to(logo, DOWN)
            banner = VGroup(logo, textb)
        
        elif mode == "e":
            logo = Text("", font="Font Awesome", color=self.conf["init"]["colors"][1]).scale(7)
            textb = Text("School Edition", font="YouTube Sans", color=WHITE)         
            textb.rescale_to_fit(logo.get_width()*0.9, 0).next_to(logo, DOWN)
            banner = VGroup(logo, textb)

        else:
            banner = VGroup()
        return(banner)


    def start_lesson(self, type="d", file=__file__):
        self.init_files(file)

        #Objs Init
        self.mobjs["logo"].set_color_by_tex(r"vec{F}", BLUE)
        self.mobjs["logo"].set_color_by_tex("m", "#56E3A7")
        self.type = type
        banner = self.get_banner(type)

        self.play(FadeIn(banner))
        self.wait(WAITTIME)
        self.play(FadeOut(banner))
        self.play(Write(self.mobjs["logo"].scale(7)), run_time=3)
        self.wait()
        self.play(self.mobjs["logo"].animate.scale(0.1).to_edge(DL))
        self.play(Create(self.mobjs["line"]))

        self.next_subt()

    def drawer(self, objs, time = 1):
        for i in objs:
            self.play(Create(i), run_time = time)

    def draw_coords(self, sx=-10, ex=10, sy=-10, ey=10):
        for x in range(sx, ex):
            for y in range(sy, ey):
                self.add(Dot(np.array([x, y, 0]), color=GREY))
    
    def next_subt(self, *anims, type = "normal", waiter = 0.5):
        conf = self.conf["subtitles"]
        type_conf = conf["types"][type]
        id = self.sub_id
        stext = self.subtitles[id]
        self.sub_id += 1

        if len(stext) >= conf["max_size"]:
            ind = stext.rfind(" ", 0, round(len(stext)/2) + 2)
            stext1 = stext[:ind]
            stext2 = stext[ind:]
        else:
            stext1 = stext
            stext2 = " "

        self.play(FadeOut(self.subtitle), run_time=0.5)

        self.subtitle[0] = Text(stext1, font_size=conf["size"], font=conf["font"], color=type_conf["color"]).shift(np.array([0, -3, 0]))
        self.subtitle[1] = Text(stext2, font_size=conf["size"], font=conf["font"], color=type_conf["color"]).next_to(self.subtitle[0], DOWN)

        self.play(Write(self.subtitle), *anims)
        self.wait(waiter)

    def multiSub(self, num, type="normal"):
        for _ in range(0, num):
            self.next_subt(type = type)
            self.wait(WAITTIME)

    def outro(self, ared):
        self.wait()
        ared.add(self.mobjs["logo"], self.mobjs["line"], self.subtitle)
        self.play(FadeOut(ared))

        conf = self.conf["outro"]
        titles = conf["titles"]
        i = 0

        for title in titles:
            um = Tex(*title).set_color_by_tex_to_color_map(self.conf["color_scheme"]["outro"]["titles"][i])
            self.play(FadeIn(um))
            self.wait(WAITTIME)
            self.play(FadeOut(um))
            self.wait(0.5)
            i += 1

        q_text = Tex(*conf["quote"]["text"])

        q_text.set_color_by_tex_to_color_map(self.conf["color_scheme"]["outro"]["quote"]["text"])

        q_author = Tex("— " + conf["quote"]["author"]).next_to(q_text, DOWN).to_edge(RIGHT)
        self.play(Write(q_text))
        self.wait(0.3)
        self.play(Write(q_author))
        self.wait(conf["quote"]["lag"])
