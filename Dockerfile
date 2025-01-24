FROM ubuntu

RUN apt-get update && apt-get install -y sudo wget python3 python3-pip git


RUN git clone https://github.com/zevisvei/sefaria_ebooks.git


WORKDIR /sefaria_ebooks


RUN sudo apt install python3.12-venv -y
RUN python3 -m venv venv
RUN ./venv/bin/pip install -r requirements.txt


RUN sudo apt install libegl1 libopengl0 libxcb-cursor0 libfreetype6 xz-utils libqt6core6 libqt6gui6t64 libqt6widgets6t64 -y


RUN sudo -v && wget -nv -O- https://download.calibre-ebook.com/linux-installer.sh | sudo sh /dev/stdin


CMD ["./venv/bin/python", "main.py"]
