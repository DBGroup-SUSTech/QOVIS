<template>
  <div class="main-page">
    <QuestionView/>
  </div>
</template>

<script>
  import QuestionView from "@/components/question-page/QuestionView";

  export default {
    name: 'QuestionPage',
    components: {
      QuestionView,
    }
  }
</script>

<style scoped>
.main-page {
  width: 100%;
  height: 100%;
}
</style>
