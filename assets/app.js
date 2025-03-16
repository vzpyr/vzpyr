'use strict';

class App {
  constructor() {
    this.id = 0;
    this.videoElement = null;
    this.audioElement = null;
    this.musicVolume = 0.04;
    this.musicFadeIn = 1000;
    this.skippedIntro = false;
    this.backgroundToggler = false;
    this.shouldIgnoreVideo = false;
    this.effects = ['bounce', 'flash', 'pulse', 'rubberBand', 'shake', 'swing', 'tada', 'wobble', 'jello'];
    this.brandDescription = [
      'welcome to mcdrive.lol'
    ];
  }

  init() {
    this.setupEventListeners();
    this.titleChanger(['m', 'mc', 'mcd', 'mcdr', 'mcdri', 'mcdriv', 'mcdrive', 'mcdrive.', 'mcdrive.l', 'mcdrive.lo', 'mcdrive.lol', 'mcdrive.lo', 'mcdrive.l', 'mcdrive.', 'mcdrive', 'mcdriv', 'mcdri', 'mcdr', 'mcd', 'mc']);
    this.updateDiscordStatus();
    setInterval(() => this.updateDiscordStatus(), 20000);
  }
  
  setupEventListeners() {
    document.addEventListener('contextmenu', (event) => event.preventDefault());
    document.body.onkeyup = (event) => this.handleKeyPress(event);
    $('.skip').click(() => this.skipIntro());
      document.querySelectorAll('[id^="back-link-"]').forEach(link => {
        link.addEventListener('click', (e) => this.toggleBack(e));
      });
    document.querySelectorAll('[id^="shop-link-"]').forEach(link => {
      link.addEventListener('click', (e) => {
        const panelId = e.target.id.replace('shop-link-', 'shop-panel-');
        this.toggleShop(e, panelId);
      });
    });
  }

  handleKeyPress(event) {
    if (event.keyCode === 32 && this.skippedIntro) {
      const mediaElements = [this.videoElement, this.audioElement];
      mediaElements.forEach(element => {
        this.backgroundToggler ? element.play() : element.pause();
      });
      this.backgroundToggler = !this.backgroundToggler;
    }
  }

  skipIntro() {
    if (this.skippedIntro) return;
    this.skippedIntro = true;
    $('.skip').addClass('fade-out');
    setTimeout(() => {
      $('.skip').remove();
    }, 500);
    $('#main').fadeOut(500, () => {
      $('#main').remove();
      this.setupMarquee();
      this.animateBrandHeader();
      this.setupBrandTyping();
      this.playMedia();
    });
  }
  

  setupMarquee() {
    $('#marquee').marquee({
      duration: 15000,
      gap: 420,
      delayBeforeStart: 1000,
      direction: 'left',
      duplicated: true,
    });
  }

  animateBrandHeader() {
    setTimeout(() => {
      $('.brand-header').animateCss(this.effects[Math.floor(Math.random() * this.effects.length)]);
    }, 200);
  }

  setupBrandTyping() {
    new Typed('#brand', {
      strings: this.brandDescription,
      typeSpeed: 40,
      loop: true,
    });
  }

  playMedia() {
    if (!this.shouldIgnoreVideo) {
      this.videoElement.play();
      this.audioElement.play();
      this.videoElement.addEventListener('timeupdate', () => {
        $.cookie('videoTime', this.videoElement.currentTime, { expires: 1 });
      }, false);
    }
    $('.marquee-container').css('visibility', 'visible').hide().fadeIn(100);
    $('.marquee-container').animateCss('zoomIn');
    $('.container').fadeIn();
    $('.background').fadeIn(200, () => {
      if (!this.shouldIgnoreVideo) $('#audio').animate({ volume: this.musicVolume }, this.musicFadeIn);
    });
  }

  toggleShop(e, panelId) {
    e.preventDefault();
    $('.index-content').addClass('fade-out');
    setTimeout(() => {
      $('.index-content').hide();
      $(`#${panelId}`).show().removeClass('fade-out').addClass('fade-in');
    }, 500);
  }

  toggleBack(e) {
    e.preventDefault();
    $('.shop-content').removeClass('fade-in').addClass('fade-out');
    setTimeout(() => {
      $('.shop-content').hide();
      $('.index-content').show().removeClass('fade-out').addClass('fade-in');
      setTimeout(() => {
        $('.shop-content').removeClass('fade-out');
        $('.index-content').removeClass('fade-in');
      }, 500);
    }, 500);
  }

  titleChanger(titles) {
    let counter = 0;
    const interval = 250;
    let timeoutId;
    const update = () => {
      document.title = titles[counter % titles.length];
      counter++;
      timeoutId = setTimeout(update, interval);
    };
    update();
    return () => clearTimeout(timeoutId);
  }

  updateDiscordStatus() {
    const userId = '737952916123549737';
    fetch(`https://api.lanyard.rest/v1/users/${userId}`)
      .then(response => response.json())
      .then(data => {
        if (!data.success) return;
        
        const user = data.data.discord_user;
        const avatar = `https://cdn.discordapp.com/avatars/${user.id}/${user.avatar}.webp?size=80`;
        const status = data.data.discord_status;
        
        document.getElementById('discord-avatar').src = avatar;
        document.getElementById('discord-username').textContent = user.global_name || user.username;
        
        const statusDot = document.getElementById('status-dot');
        statusDot.className = `status-dot status-${status}`;
        
        const activityEl = document.getElementById('discord-activity');
        if (data.data.listening_to_spotify) {
          activityEl.textContent = `🎶 ${data.data.spotify.song} by ${data.data.spotify.artist}`;
        } else if (data.data.activities.length > 0) {
          const activity = data.data.activities[0];
          const activityTypes = {
            0: 'Playing',
            1: 'Streaming',
            2: 'Listening to',
            3: 'Watching',
            4: 'Custom',
            5: 'Competing in'
          };
          const activityType = activityTypes[activity.type] || 'Playing';
          activityEl.textContent = `${activityType} ${activity.name}`;
        } else {
          activityEl.textContent = status.charAt(0).toUpperCase() + status.slice(1);
        }
      });
  }}
  
$.fn.extend({
  animateCss: function (animationName) {
    const animationEnd = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';
    this.addClass(`animated ${animationName}`).one(animationEnd, () => {
      $(this).removeClass(`animated ${animationName}`);
    });
    return this;
  },
});

const app = new App();
$(document).ready(() => app.init());