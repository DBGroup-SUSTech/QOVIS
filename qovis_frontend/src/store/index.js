import Vue from 'vue';
import Vuex from 'vuex';
import test from '@/store/module/test';
import trace from "@/store/module/trace";
import native from "@/store/module/native"
import timeline from "@/store/module/timeline"
import seq from "@/store/module/seq"
import seq2 from "@/store/module/seq2"
import probe from "@/store/module/probe"
import question from "@/store/module/question"

Vue.use(Vuex)

// const debug = process.env.NODE_ENV !== 'production'

export default new Vuex.Store({
  modules: {
    trace, native, timeline, seq, seq2, test, probe, question,
  },
  // strict: debug,
  strict: false,
})
