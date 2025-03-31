<template>
    <div class="app-container">
        <el-form
            :model="queryParams"
            ref="queryRef"
            :inline="true"
            v-show="showSearch"
            label-width="68px"
        >
            <el-form-item label="表单名称" prop="name">
                <el-input
                    v-model="queryParams.name"
                    placeholder="请输入表单名称"
                    clearable
                    @keyup.enter="handleQuery"
                />
            </el-form-item>
            <el-form-item>
                <el-button type="primary" icon="Search" @click="handleQuery"
                    >搜索</el-button
                >
                <el-button icon="Refresh" @click="resetQuery">重置</el-button>
            </el-form-item>
        </el-form>

        <el-card class="base-table" ref="fullTable">
            <TableSetup
                ref="tSetup"
                @onStripe="onStripe"
                @onRefresh="onRefresh"
                @onChange="onChange"
                @onfullTable="onfullTable"
                @onSearchChange="onSearchChange"
                :columns="columns"
                :isTable="isTable"
            >
                <template v-slot:operate>
                    <el-button
                        type="primary"
                        plain
                        icon="Plus"
                        @click="handleAdd"
                        v-hasPermi="['sys:form:add']"
                        >新增</el-button
                    >
                    <el-button
                        type="success"
                        plain
                        icon="Edit"
                        :disabled="single"
                        @click="handleUpdate"
                        v-hasPermi="['sys:form:edit']"
                        >修改</el-button
                    >
                    <el-button
                        type="danger"
                        plain
                        icon="Delete"
                        :disabled="multiple"
                        @click="handleDelete"
                        v-hasPermi="['sys:form:remove']"
                        >删除</el-button
                    >
                    <el-button
                        type="warning"
                        plain
                        icon="Download"
                        @click="handleExport"
                        v-hasPermi="['sys:form:export']"
                        >导出</el-button
                    >
                </template>
            </TableSetup>
            <auto-table
                ref="multipleTable"
                class="mytable"
                :tableData="formList"
                :columns="columns"
                :loading="loading"
                :stripe="stripe"
                :tableHeight="tableHeight"
                @onColumnWidthChange="onColumnWidthChange"
                @onSelectionChange="handleSelectionChange"
            >
                <template #dataCount="{ row }">
                    <span>
                        <el-button width="20" round @click="showFormData(row)">
                            <el-link type="primary">{{
                                row.dataCount
                            }}</el-link>
                        </el-button>
                    </span>
                </template>
                <template #createTime="{ row }">
                    <span>{{ parseTime(row.createTime, '{y}-{m}-{d}') }}</span>
                </template>

                <template #updateTime="{ row }">
                    <span>{{ parseTime(row.updateTime, '{y}-{m}-{d}') }}</span>
                </template>
                <template #operate="{ row }">
                    <el-button
                        link
                        type="primary"
                        icon="Download"
                        @click="handleDownload(row)"
                        v-hasPermi="['sys:form:remove']"
                        >下载</el-button
                    >
                    <el-button
                        link
                        type="primary"
                        icon="Edit"
                        @click="handleUpdate(row)"
                        v-hasPermi="['sys:form:edit']"
                        >修改</el-button
                    >
                    <el-button
                        link
                        type="primary"
                        icon="Delete"
                        @click="handleDelete(row)"
                        v-hasPermi="['sys:form:remove']"
                        >删除</el-button
                    >
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

        <!-- 添加或修改系统表单对话框 -->
        <el-dialog :title="title" v-model="open" width="1200px" append-to-body>
            <build-index
                :formDataJson="form.formData"
                :formConfJson="form.formConf"
                :drawingListJson="form.drawingList"
                :generateConfJson="form.generateConf"
                @onFormSave="onFormSave"
            />
        </el-dialog>

        <form-data-dialog
            v-model="openFormData"
            width="1000px"
            :formId="detailFormId"
            :formName="detailFormName"
        />
    </div>
</template>

<script setup name="SysForm">
import {
    listForm,
    getForm,
    delForm,
    addForm,
    updateForm
} from '@/api/system/form'
import { listAllTable } from '@/api/system/table'
import TableSetup from '@/components/TableSetup'
import AutoTable from '@/components/AutoTable'
import Download from '@/plugins/download'
import BuildIndex from './BuildIndex.vue'
import FormDataDialog from './FormDataDialog.vue'

const { proxy } = getCurrentInstance()

const formList = ref([])
const open = ref(false)
const loading = ref(true)
const showSearch = ref(true)
const ids = ref([])
const single = ref(true)
const multiple = ref(true)
const total = ref(0)
const title = ref('')
const openFormData = ref(false)
const detailFormId = ref(null)
const detailFormName = ref(null)

const columns = ref([])
const stripe = ref(true)
const isTable = ref(true)
const tableHeight = ref(500)

const data = reactive({
    form: {},
    queryParams: {
        pageNum: 1,
        pageSize: 10,
        name: null
    },
    rules: {
        content: [
            { required: true, message: '表单代码不能为空', trigger: 'blur' }
        ],
        createBy: [
            { required: true, message: '创建者不能为空', trigger: 'blur' }
        ],
        deptId: [
            { required: true, message: '部门id不能为空', trigger: 'blur' }
        ],
        formConf: [
            { required: true, message: '表单配置不能为空', trigger: 'blur' }
        ],
        formData: [
            { required: true, message: '表单内容不能为空', trigger: 'blur' }
        ],
        generateConf: [
            { required: true, message: '生成配置不能为空', trigger: 'blur' }
        ],
        name: [{ required: true, message: '表单名称不能为空', trigger: 'blur' }]
    }
})

const { queryParams, form, rules } = toRefs(data)

/** 查询系统表单列表 */
function getList() {
    loading.value = true
    listForm(queryParams.value).then((response) => {
        formList.value = response.rows
        total.value = response.total
        loading.value = false
    })
}

function getColumns() {
    listAllTable({ tableName: 'sys_form' })
        .then((response) => {
            columns.value = response.data
        })
        .then(() => {
            getList()
        })
}

// 取消按钮
function cancel() {
    open.value = false
    reset()
}

// 表单重置
function reset() {
    form.value = {
        content: null,
        createBy: null,
        createTime: null,
        delFlag: null,
        deptId: null,
        formConf: null,
        formData: null,
        generateConf: null,
        drawingList: null,
        id: null,
        name: null,
        updateTime: null
    }
    // proxy.resetForm('formRef')
}

/** 搜索按钮操作 */
function handleQuery() {
    queryParams.value.pageNum = 1
    getList()
}

/** 重置按钮操作 */
function resetQuery() {
    proxy.resetForm('queryRef')
    handleQuery()
}

// 多选框选中数据
function handleSelectionChange(selection) {
    ids.value = selection.map((item) => item.id)
    single.value = selection.length != 1
    multiple.value = !selection.length
}

/** 新增按钮操作 */
function handleAdd() {
    reset()
    open.value = true
    title.value = '添加系统表单'
}

/** 修改按钮操作 */
function handleUpdate(row) {
    reset()
    const sysFormId = row.id || ids.value
    getForm(sysFormId).then((response) => {
        form.value = response.data
        open.value = true
        title.value = '修改系统表单'
    })
}

function handleDownload(row) {
    const blob = new Blob([row.content], { type: 'text/plain;charset=utf-8' })
    Download.saveAs(blob, row.name + '.vue')
    proxy.$modal.msgSuccess('下载成功')
}

/** 提交按钮 */
function submitForm() {
    if (form.value.content == null) {
        proxy.$modal.msgError('表单代码不能为空')
        return
    }
    if (form.value.name == null) {
        proxy.$modal.msgError('表单备注不能为空')
        return
    }
    if (form.value.id != null) {
        updateForm(form.value).then((response) => {
            proxy.$modal.msgSuccess('修改成功')
            open.value = false
            getList()
        })
    } else {
        addForm(form.value).then((response) => {
            proxy.$modal.msgSuccess('新增成功')
            open.value = false
            getList()
        })
    }
}

/** 删除按钮操作 */
function handleDelete(row) {
    const _ids = row.id || ids.value
    proxy.$modal
        .confirm('是否确认删除系统表单编号为"' + _ids + '"的数据项？')
        .then(function () {
            return delForm(_ids)
        })
        .then(() => {
            getList()
            proxy.$modal.msgSuccess('删除成功')
        })
        .catch(() => {})
}

/** 导出按钮操作 */
function handleExport() {
    proxy.download(
        'sys/form/export',
        {
            ...queryParams.value
        },
        `form_${new Date().getTime()}.xlsx`
    )
}

//表格全屏
function onfullTable() {
    proxy.$refs.tSetup.onFull(proxy.$refs.fullTable.$el)
}
//表格刷新
function onRefresh() {
    getList()
}
//搜索框显示隐藏
function onSearchChange() {
    showSearch.value = !showSearch.value
}

function onStripe(val) {
    stripe.value = val
}
//改变表头数据
function onChange(val) {
    columns.value = val
}

//改变表格宽度
function onColumnWidthChange(column) {
    proxy.$refs.tSetup.tableWidth(column)
}

function onFormSave(code, formData, formConf, generateConf, drawingList) {
    form.value.content = code
    form.value.formConf = JSON.stringify(formConf)
    form.value.formData = JSON.stringify(formData)
    form.value.generateConf = JSON.stringify(generateConf)
    form.value.drawingList = JSON.stringify(drawingList)
    form.value.name = formConf.remark
    submitForm()
}

function showFormData(row) {
    detailFormId.value = row.id
    detailFormName.value = row.name
    openFormData.value = true
}

getColumns()
</script>