<template>
  <div class="native">
    <div v-for="(plan, i) in plans" :key="updateCnt + '-' + i" class="node-container">
      <div class="metrics-container" :style="{background: getPlanColor(plan)}">
        <div v-for="[k, v] in getPlanMetaInfo(plan)" :key="k">
          {{ `${k}: ${v}` }}
        </div>
      </div>
      <div class="plan-container">
        <div class="metrics-container">
          <div v-for="[k, v] in getPlanInfoPairs(plan)" :key="k">
            {{ `${k}: ${v}` }}
          </div>
        </div>
        <div class="plan-dag-container">
          <Dag :plan="plan"></Dag>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import {mapState} from "vuex"
import {getColor} from "@/js/common"
import Dag from "@/components/common/Dag"

export default {
  name: 'Native',
  components: {
    Dag
  },
  data() {
    return {
      updateCnt: 0,
    }
  },
  mounted() {
  },
  methods: {
    /**
     * @param {Plan} plan
     */
    getPlanColor(plan) {
      return getColor(plan.meta.type)
    },
    /**
     * @param {Plan} plan
     * @returns {[string, *][]}
     */
    getPlanMetaInfo(plan) {
      return plan.meta.getInfoPairs()
    },
    /**
     * @param {Plan} plan
     * @returns {[string, *][]}
     */
    getPlanInfoPairs(plan) {
      return [
          ['pid', plan.pid]
      ]
    }
  },
  watch: {
  },
  computed: {
    ...mapState('native', {
      plans: state => state.plans
    }),
  }
}
</script>

<style scoped>
.native {
  height: 100%;
  width: 100%;
  overflow: auto;

  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
}
.node-container {
  display: flex;
  flex-direction: column;

  margin: 10px;
  border: 2px solid gray;
}
.plan-container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: flex-start;
}
.metrics-container {
  flex-grow: 0;
  text-align: left;
}
</style>
