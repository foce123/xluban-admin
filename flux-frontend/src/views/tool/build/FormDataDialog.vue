<template>
    <el-dialog
        v-model="open"
        width="900px"
        :title="formName"
        @open="onOpen"
        @close="onClose"
    >
        <el-card class="base-table" ref="fullTable">
            <TableSetup
                ref="tSetup"
                @onRefresh="onRefresh"
                @onChange="onChange"
                :columns="columns"
                :isTable="isTable"
            >
                <template v-slot:operate>
                    <el-button
                        type="warning"
                        plain
                        icon="Download"
                        @click="handleExport"
                        v-hasPermi="['sys:form_data:export']"
                        >导出</el-button
                    >
                </template>
            </TableSetup>
            <auto-table
                ref="multipleTable"
                class="mytable"
                :tableData="formDataList"
                :columns="columns"
                :loading="loading"
                :stripe="stripe"
                :tableHeight="tableHeight"
                @onColumnWidthChange="onColumnWidthChange"
                @onSelectionChange="handleSelectionChange"
            >
                <template #createTime="{ row }">
                    <span>{{ parseTime(row.createTime, '{y}-{m}-{d}') }}</span>
                </template>

                <template #updateTime="{ row }">
                    <span>{{ parseTime(row.updateTime, '{y}-{m}-{d}') }}</span>
                </template>
            </auto-table>
            <div class="table-pagination">
                <pagination
                    v-show="total > 0"
                    :total="total"
                    v-model:page="queryParams.pageNum"
                    v-model:limit="queryParams.pageSize"
                    @pagination="getList"
                />
            </div>
        </el-card>
        <template #footer>
            <el-button @click="onClose">关闭</el-button>
        </template>
    </el-dialog>
</template>

<script setup>
import { listForm_data } from '@/api/system/form_data'
import TableSetup from '@/components/TableSetup'
import AutoTable from '@/components/AutoTable'
const { proxy } = getCurrentInstance()
const data = reactive({
    queryParams: {
        pageNum: 1,
        pageSize: 10,
        formId: null
    }
})

const loading = ref(true)
const total = ref(0)
const columns = ref([])
const formDataList = ref([])
const open = defineModel()
const props = defineProps({
    formId: Number,
    formName: String
})
const { queryParams } = toRefs(data)
const emit = defineEmits(['confirm'])

const codeTypeForm = ref()
function onClose() {
    open.value = false
}

/** 查询表单数据列表 */
function getList() {
    loading.value = true
    queryParams.formId = props.formId
    listForm_data(queryParams.value).then((response) => {
        columns.value = convetColumns(JSON.parse(response.rows[0].formData))
        formDataList.value = convertDataList(response.rows)
        total.value = response.total
        loading.value = false
    })
}

function convetColumns(row) {
    const columns = []
    for (const key in row) {
        columns.push({
            label: key,
            prop: key,
            align: 'center',
            fieldName: key,
            fixed: 0,
            width: 150,
            sequence: 0,
            show: '1',
            sortable: '0',
            tooltip: '1'
        })
    }
    return columns
}

function convertDataList(rows) {
    const list = []
    for (const row of rows) {
        const item = JSON.parse(row.formData)
        list.push(item)
    }
    return list
}

function onOpen() {
    getList()
}

/** 导出按钮操作 */
function handleExport() {
    const params = {
        formId: props.formId
    }
    proxy.download(
        'sys/form_data/export',
        {
            ...params.value
        },
        `form_${new Date().getTime()}.xlsx`
    )
}
</script>