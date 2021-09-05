<template>
  <div id="app">
    <button id="mic_btn" @click="record = !record">
        {{record?'👂':'🎙️'}}
    </button>

    <vue-web-speech
      v-model="record"
      @results="onResults"
      @unrecognized="unrecognized"
    >
    </vue-web-speech>

    <VueBotUI
      :messages="msg"
      :options="botOptions"
      :bot-typing="locking"
      :input-disable="locking"
      @msg-send="msgSender"
    />

    <vue-web-speech-synth
      v-model="agentSpeak"
      :voice="synthVoice"
      :text="synthText"
      @list-voices="listVoices"
    />

  </div>
</template>

<script>
import { VueBotUI } from 'vue-bot-ui'
import axios from "axios";

export default {
  name: 'App',
  components: {
    VueBotUI,
  },
  data () {
    return {
      // apiEndpoint: "http://localhost:8081/query",
      apiEndpoint: "/query",
      record: false,
      results: null,
      voiceList: [],
      agentSpeak: false,
      synthVoice: null,
      synthText: 'This is Siwi, what can I do for you?',
      msg: [],
      locking: false,
      botOptions: {
        botTitle: "Siwi",
        botAvatarImg: "https://www.shareicon.net/data/256x256/2016/01/05/233432_alfred_256x256.png",
        msgBubbleBgUser: "#657b83",
        boardContentBg: "#073642",
        colorScheme: "#002b36",
      },
    }
  },
  mounted() {
      this.msg.push({
        agent: "bot",
        type: "text",
        text: "This is Siwi, what can I do for you?",
      });
  },
  methods: {
    onResults (data) {
      this.results = data;
      this.locking = true;

      this.msg.push({
        agent: "user",
        type: "text",
        text: data[0],
      });

      this.locking = true;
      console.log(data[0]);
      axios.post(this.apiEndpoint, { "question": data[0] }).then((response) => {
        console.log(response.data);

        this.msg.push({
          agent: "bot",
          type: "text",
          text: response.data.answer,
        });

        this.synthText = response.data.answer;
        this.agentSpeak = true;
      });
      this.locking = false;

    },
    unrecognized () {
      this.synthText = 'Opps, I Dont understand you';
      this.agentSpeak = true;
    },
    listVoices (list) {
      this.voiceList = list;
    },
    msgSender(data) {
      this.msg.push({
        agent: "user",
        type: "text",
        text: data.text,
      });

      this.locking = true;

      axios.post(this.apiEndpoint, { "question": data.text }).then((response) => {
        console.log(response);

        this.msg.push({
          agent: "bot",
          type: "text",
          text: response.data.answer,
        });

        this.synthText = response.data.answer;
        this.agentSpeak = true;

        this.locking = false;
      });
    },
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
#mic_btn {
  background-color: #073642;
  border: none;
  color: white;
  position: fixed;
  bottom: 20px;
  right: 330px;
  padding: 15px 32px;
  text-align: center;
  font-size: 12px;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  box-shadow: 0 2px 3px 0 rgba(0,0,0,0.2), 0 1px 4px 0 rgba(0,0,0,0.19);
}
</style>