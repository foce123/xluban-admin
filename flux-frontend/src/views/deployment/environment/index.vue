<template>
    <div class="app-container">
        <el-form
            :model="queryParams"
            ref="queryRef"
            :inline="true"
            v-show="showSearch"
        >
            <el-form-item label="环境编码" prop="envCode">
                <el-input
                    v-model="queryParams.envCode"
                    placeholder="请输入环境编码"
                    clearable
                    style="width: 200px"
                    @keyup.enter="handleQuery"
                />
            </el-form-item>
            <el-form-item label="环境名称" prop="envName">
                <el-input
                    v-model="queryParams.envName"
                    placeholder="请输入环境名称"
                    clearable
                    style="width: 200px"
                    @keyup.enter="handleQuery"
                />
            </el-form-item>
            <el-form-item label="状态" prop="status">
                <el-select
                    v-model="queryParams.status"
                    placeholder="环境状态"
                    clearable
                    style="width: 200px"
                >
                    <el-option
                        v-for="dict in sys_normal_disable"
                        :key="dict.value"
                        :label="dict.label"
                        :value="dict.value"
                    />
                </el-select>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" icon="Search" @click="handleQuery"
                    >搜索</el-button
                >
                <el-button icon="Refresh" @click="resetQuery">重置</el-button>
            </el-form-item>
        </el-form>

        <el-row :gutter="10" class="mb8">
            <el-col :span="1.5">
                <el-button
                    type="primary"
                    plain
                    icon="Plus"
                    @click="handleAdd"
                    v-hasPermi="['deployment:environment:add']"
                    >新增</el-button
                >
            </el-col>
            <el-col :span="1.5">
                <el-button
                    type="success"
                    plain
                    icon="Edit"
                    :disabled="single"
                    @click="handleUpdate"
                    v-hasPermi="['deployment:environment:edit']"
                    >修改</el-button
                >
            </el-col>
            <el-col :span="1.5">
                <el-button
                    type="danger"
                    plain
                    icon="Delete"
                    :disabled="multiple"
                    @click="handleDelete"
                    v-hasPermi="['deployment:environment:remove']"
                    >删除</el-button
                >
            </el-col>
            <el-col :span="1.5">
                <el-button
                    type="warning"
                    plain
                    icon="Download"
                    @click="handleExport"
                    v-hasPermi="['deployment:environment:export']"
                    >导出</el-button
                >
            </el-col>
            <right-toolbar
                v-model:showSearch="showSearch"
                @queryTable="getList"
            ></right-toolbar>
        </el-row>

        <el-table
            v-loading="loading"
            :data="envList"
            @selection-change="handleSelectionChange"
        >
            <el-table-column type="selection" width="55" align="center" />
            <el-table-column label="环境编号" align="center" prop="envId" />
            <el-table-column label="环境编码" align="center" prop="envCode" />
            <el-table-column label="环境名称" align="center" prop="envName" />
            <el-table-column label="环境排序" align="center" prop="envSort" />
            <el-table-column label="状态" align="center" prop="status">
                <template #default="scope">
                    <dict-tag
                        :options="sys_normal_disable"
                        :value="scope.row.status"
                    />
                </template>
            </el-table-column>
            <el-table-column
                label="创建时间"
                align="center"
                prop="createTime"
                width="180"
            >
                <template #default="scope">
                    <span>{{ parseTime(scope.row.createTime) }}</span>
                </template>
            </el-table-column>
            <el-table-column
                label="操作"
                width="180"
                align="center"
                class-name="small-padding fixed-width"
            >
                <template #default="scope">
                    <el-button
                        link
                        type="primary"
                        icon="Edit"
                        @click="handleUpdate(scope.row)"
                        v-hasPermi="['deployment:environment:edit']"
                        >修改</el-button
                    >
                    <el-button
                        link
                        type="primary"
                        icon="Delete"
                        @click="handleDelete(scope.row)"
                        v-hasPermi="['deployment:environment:remove']"
                        >删除</el-button
                    >
                </template>
            </el-table-column>
        </el-table>

        <pagination
            v-show="total > 0"
            :total="total"
            v-model:page="queryParams.pageNum"
            v-model:limit="queryParams.pageSize"
            @pagination="getList"
        />

        <!-- 添加或修改环境对话框 -->
        <el-dialog :title="title" v-model="open" width="500px" append-to-body>
            <el-form
                ref="envRef"
                :model="form"
                :rules="rules"
                label-width="80px"
            >
                <el-form-item label="环境名称" prop="envName">
                    <el-input
                        v-model="form.envName"
                        placeholder="请输入环境名称"
                    />
                </el-form-item>
                <el-form-item label="环境编码" prop="envCode">
                    <el-input
                        v-model="form.envCode"
                        placeholder="请输入编码名称"
                    />
                </el-form-item>
                <el-form-item label="环境顺序" prop="envSort">
                    <el-input-number
                        v-model="form.envSort"
                        controls-position="right"
                        :min="0"
                    />
                </el-form-item>
                <el-form-item label="环境状态" prop="status">
                    <el-radio-group v-model="form.status">
                        <el-radio
                            v-for="dict in sys_normal_disable"
                            :key="dict.value"
                            :value="dict.value"
                            >{{ dict.label }}</el-radio
                        >
                    </el-radio-group>
                </el-form-item>
                <el-form-item label="备注" prop="remark">
                    <el-input
                        v-model="form.remark"
                        type="textarea"
                        placeholder="请输入内容"
                    />
                </el-form-item>
            </el-form>
            <template #footer>
                <div class="dialog-footer">
                    <el-button type="primary" @click="submitForm"
                        >确 定</el-button
                    >
                    <el-button @click="cancel">取 消</el-button>
                </div>
            </template>
        </el-dialog>
    </div>
</template>

<script setup name="Env">
import {
    listEnv,
    addEnv,
    delEnv,
    getEnv,
    updateEnv
} from '@/api/deployment/environment'
const { proxy } = getCurrentInstance()
const { sys_normal_disable } = proxy.useDict('sys_normal_disable')

const envList = ref([])
const open = ref(false)
const loading = ref(true)
const showSearch = ref(true)
const ids = ref([])
const single = ref(true)
const multiple = ref(true)
const total = ref(0)
const title = ref('')

const data = reactive({
    form: {},
    queryParams: {
        pageNum: 1,
        pageSize: 10,
        envCode: undefined,
        envName: undefined,
        status: undefined
    },
    rules: {
        envName: [
            { required: true, message: '环境名称不能为空', trigger: 'blur' }
        ],
        envCode: [
            { required: true, message: '环境编码不能为空', trigger: 'blur' }
        ],
        envSort: [
            { required: true, message: '环境顺序不能为空', trigger: 'blur' }
        ]
    }
})

const { queryParams, form, rules } = toRefs(data)

/** 查询环境列表 */
function getList() {
    loading.value = true
    listEnv(queryParams.value).then((response) => {
        envList.value = response.rows
        total.value = response.total
        loading.value = false
    })
}
/** 取消按钮 */
function cancel() {
    open.value = false
    reset()
}
/** 表单重置 */
function reset() {
    form.value = {
        envId: undefined,
        envCode: undefined,
        envName: undefined,
        envSort: 0,
        status: '0',
        remark: undefined
    }
    proxy.resetForm('envRef')
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
/** 多选框选中数据 */
function handleSelectionChange(selection) {
    ids.value = selection.map((item) => item.envId)
    single.value = selection.length != 1
    multiple.value = !selection.length
}
/** 新增按钮操作 */
function handleAdd() {
    reset()
    open.value = true
    title.value = '添加环境'
}
/** 修改按钮操作 */
function handleUpdate(row) {
    reset()
    const envId = row.envId || ids.value
    getEnv(envId).then((response) => {
        form.value = response.data
        open.value = true
        title.value = '修改环境'
    })
}
/** 提交按钮 */
function submitForm() {
    proxy.$refs['envRef'].validate((valid) => {
        if (valid) {
            if (form.value.envId != undefined) {
                updateEnv(form.value).then((response) => {
                    proxy.$modal.msgSuccess('修改成功')
                    open.value = false
                    getList()
                })
            } else {
                addEnv(form.value).then((response) => {
                    proxy.$modal.msgSuccess('新增成功')
                    open.value = false
                    getList()
                })
            }
        }
    })
}
/** 删除按钮操作 */
function handleDelete(row) {
    const envIds = row.envId || ids.value
    proxy.$modal
        .confirm('是否确认删除环境编号为"' + envIds + '"的数据项？')
        .then(function () {
            return delEnv(envIds)
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
        'deployment/environment/export',
        {
            ...queryParams.value
        },
        `env_${new Date().getTime()}.xlsx`
    )
}

getList()
</script>
