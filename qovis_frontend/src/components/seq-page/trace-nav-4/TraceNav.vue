<template>
  <div class="trace-nav">
    <svg id="trace-svg"
         ref="svgEl"
         :width="width" :height="height">
      <g v-if="visTraceTree" class="trace-root-group"
         :transform="(toEnlarge ? 'scale(' + enlargeFactor + ')' : '') + `translate(${[visTraceTree.startX + treeMargin, visTraceTree.startY + treeMargin * 3]})`">
        <g class="action-group">
          <TraceNavNode :vis-trace-tree="visTraceTree"
                        :vis-trace-node="treeRoot"/>
        </g>
        <g class="plan-block-group">
          <g v-for="(block, idx) in visTraceTree.planBlocks" :key="idx"
             class="plan-block">
            <rect :x="block.centerX - block.radius"
                  :y="block.topY - block.radius"
                  :rx="block.radius"
                  :ry="block.radius"
                  :width="block.radius * 2"
                  :height="block.rectHeight + block.radius * 2"
                  :fill="'#9a9a9a'"
                  :stroke="'#ffffff'"
                  stroke-width="5">
              <title>{{ getPlanBlockName(block) }}</title>
            </rect>
          </g>
        </g>
        <g class="plan-dag-group">
          <PlanView :vis-trace-tree="visTraceTree"/>
        </g>
        <g class="transform-path-group">
          <g v-for="(transPath, i) in visTransPaths"
             :key="i"
             class="transform-list-group"
             :transform="`translate(${[planPadding, planPadding]})`">
            <g v-for="(link, j) in transPath.links"
               :key="j"
               class="transform-item"
               @mouseenter="enterLink(link)"
               @mouseleave="leaveLink(link)"
               @click="clickLink(link)">
              <title>{{ link.getTooltipText() }}</title>
              <path v-show="showLink(link)"
                    :d="link.path"
                    stroke-width="3"
                    :stroke="link.color"
                    :stroke-dasharray="link.origin.kind === 'peq' ? '10,8' : 'none'"
                    opacity="0.5"
                    fill="none"/>
            </g>
          </g>
        </g>
        <g class="transform-path-group-fix-highlight">
          <g v-for="(transPath, i) in visTransPaths"
             :key="i"
             class="transform-list-group"
             :transform="`translate(${[planPadding, planPadding]})`">
            <g v-for="(link, j) in transPath.links"
               :key="j"
               class="transform-item"
               @mouseenter="enterLink(link)"
               @mouseleave="leaveLink(link)"
               @click="clickLink(link)">
              <title>{{ link.getTooltipText() }}</title>
              <path v-if="link.isFixHighlight"
                    :d="link.path"
                    :stroke-width="3"
                    :stroke="getFixHighlightColor(link)"
                    :stroke-dasharray="link.origin.kind !== 'ch' ? '10,8' : 'none'"
                    fill="none"/>
              <g v-if="link.fixed"
                 :transform="`translate(${[link.iconPoint.x - 10, link.iconPoint.y - 10]})`">
                <svg t="1710227415094" class="icon" viewBox="0 0 1025 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1464" xmlns:xlink="http://www.w3.org/1999/xlink" width=20 height="20">
                  <circle cx="512" cy="512" r="250" fill="white" p-id="11604"></circle>
                  <path :fill="getIconHighlightColor(link)"
                        d="M511.999 225.386C177.707 225.386 2.441 472.773 2.441 512c0 39.226 175.264 286.614 509.558 286.614 334.273 0 509.558-247.388 509.558-286.614 0-39.227-175.285-286.614-509.558-286.614z m0 507.089c-125.087 0-226.477-98.71-226.477-220.475 0-121.787 101.39-220.475 226.477-220.475 125.088 0 226.477 98.69 226.477 220.475 0 121.765-101.39 220.475-226.477 220.475z m0-220.475c-20.754-22.889 33.796-110.258 0-110.258-62.554 0-113.228 49.387-113.228 110.258 0 60.871 50.673 110.217 113.228 110.217 62.513 0 113.23-49.345 113.23-110.217 0-27.989-95.585 19.427-113.23 0z" p-id="19679"></path>
                </svg>
              </g>
            </g>
          </g>
        </g>
        <g class="transform-path-group-highlight">
          <g v-for="(transPath, i) in visTransPaths"
             :key="i"
             class="transform-list-group"
             :transform="`translate(${[planPadding, planPadding]})`">
            <g v-for="(link, j) in transPath.links"
               :key="j"
               class="transform-item">
              <title>{{ link.getTooltipText() }}</title>
              <path v-if="link.isHighlight"
                    :d="link.path"
                    :stroke-width="5"
                    :stroke="getHighlightColor(link)"
                    :stroke-dasharray="link.origin.kind !== 'ch' ? '10,8' : 'none'"
                    fill="none"/>
              <g v-if="link.isHighlight && link.fixed"
                 :transform="`translate(${[link.iconPoint.x - 10, link.iconPoint.y - 10]})`">
                <svg t="1710227415094" class="icon" viewBox="0 0 1025 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1464" xmlns:xlink="http://www.w3.org/1999/xlink" width=20 height="20">
                  <circle cx="512" cy="512" r="250" fill="white" p-id="11604"></circle>
                  <path :fill="getIconFixHighlightColor(link)"
                        d="M511.999 225.386C177.707 225.386 2.441 472.773 2.441 512c0 39.226 175.264 286.614 509.558 286.614 334.273 0 509.558-247.388 509.558-286.614 0-39.227-175.285-286.614-509.558-286.614z m0 507.089c-125.087 0-226.477-98.71-226.477-220.475 0-121.787 101.39-220.475 226.477-220.475 125.088 0 226.477 98.69 226.477 220.475 0 121.765-101.39 220.475-226.477 220.475z m0-220.475c-20.754-22.889 33.796-110.258 0-110.258-62.554 0-113.228 49.387-113.228 110.258 0 60.871 50.673 110.217 113.228 110.217 62.513 0 113.23-49.345 113.23-110.217 0-27.989-95.585 19.427-113.23 0z" p-id="19679"></path>
                </svg>
              </g>
            </g>
          </g>
        </g>
      </g>
    </svg>
  </div>
</template>

<script>
/* eslint-disable */
import {mapMutations, mapState} from 'vuex'
import {VisTraceTree} from "@/js/trace/VisTraceTree"
import PlanView from "@/components/seq-page/trace-nav-4/PlanView"
import TraceNavNode from "@/components/seq-page/trace-nav-4/TraceNavNode"

const ENLARGE_FACTOR = 4

export default {
  name: 'TraceNav',
  components: {
    PlanView,
    TraceNavNode,
  },
  props: {
    visTraceTree: VisTraceTree,
  },
  data() {
    return {}
  },
  mounted() {
    this.mountSvgEl(this.$refs.svgEl)
  },
  methods: {
    ...mapMutations('trace', [
      'changeFixHighlightObject',
      'mountSvgEl',
    ]),
    getPlanBlockName(block) {
      return `plan#${block.visPlan.origin.pid}`
    },
    showLink(link) {
      return false;
      // if (!this.transSupportEnabled) {
      //   return false
      // }
      // return (link.origin.kind !== 'eq' || this.showUnchangeLink) && link.origin.kind !== 'peq'
    },
    getHighlightColor(link) {
      return this.color.highlight
      // return link.origin.kind === 'ch' ? this.color.highlight : this.color.normal
    },
    getFixHighlightColor(link) {
      return this.color.fixHighlight
      // return link.origin.kind === 'ch' ? this.color.fixHighlight : this.color.normal
    },
    getIconHighlightColor(link) {
      return this.color.fixHighlight
    },
    getIconFixHighlightColor(link) {
      return this.color.highlight
    },
    enterLink(link) {
      if (!this.transSupportEnabled) {
        return
      }
      link.highlight()
    },
    leaveLink(link) {
      if (!this.transSupportEnabled) {
        return
      }
      if (this.hoverDelay) {
        setTimeout(() => {
          link.unhighlight()
        }, 2000)
      } else {
        link.unhighlight()
      }
    },
    /**
     * @param {VisTransLink} link
     */
    clickLink(link) {
      if (!this.transSupportEnabled) {
        return
      }
      if (link.fixed) {
        this.changeFixHighlightObject(null)
        if (!this.showLink(link)) {   // !!
          link.unhighlight()
        }
      } else {
        this.changeFixHighlightObject(link)
      }
    },
  },
  computed: {
    ...mapState('trace', {
      color: state => state.configV3.color,
      treeMargin: state => state.configV3.traceTree.margin,
      planPadding: state => state.configV3.plan.padding,
      showUnchangeLink: state => state.showUnchangeLink,
      transSupportEnabled: state => state.transSupportEnabled,
      toEnlarge: state => state.toEnlarge,
      enlargeFactor: state => state.configV3.enlargeFactor,
      hoverDelay: state => state.hoverDelay,
    }),
    width() {
      const value = (this.visTraceTree?.width ?? 0) + this.treeMargin * 2
      if (this.toEnlarge) {
        return this.enlargeFactor * value
      }
      return value
    },
    height() {
      const value = (this.visTraceTree?.height ?? 0) + this.treeMargin * 4
      if (this.toEnlarge) {
        return this.enlargeFactor * value
      }
      return value
    },
    treeRoot() {
      return this.visTraceTree?.root ?? null
    },
    visTransPaths() {
      return this.visTraceTree?.visTransPaths ?? []
    },
  }
}
</script>

<style scoped>
.trace-nav {
  padding: 10px;
}
.transform-item {
  cursor: pointer;
}
.transform-path-group-highlight {
  pointer-events: none;
}
</style>
