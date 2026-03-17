import { InboxOutlined, UploadOutlined } from '@ant-design/icons'
import { Alert, Button, Card, Col, Descriptions, Divider, Row, Space, Table, Typography, Upload, message } from 'antd'
import { useState } from 'react'
import api, { useMock } from '../api'

const { Dragger } = Upload

export default function UploadPage() {
  const [fileList, setFileList] = useState([])
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])

  const onUpload = async () => {
    const f = fileList[0]?.originFileObj
    if (!f) {
      message.warning('请先选择一个 license 文件')
      return
    }

    if (useMock) {
      const mockResult = {
        ok: true,
        filename: f.name,
        parsed_features: 12,
        server: 'snps-lic-01',
        port: 27000,
      }
      setResult(mockResult)
      setHistory((prev) => [{ key: Date.now(), filename: f.name, parsed: 12, server: 'snps-lic-01', time: new Date().toLocaleString() }, ...prev])
      message.success('Mock 上传完成')
      return
    }

    const fd = new FormData()
    fd.append('file', f)
    setUploading(true)
    try {
      const { data } = await api.post('/license/upload', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setResult(data)
      setHistory((prev) => [{ key: Date.now(), filename: data.filename, parsed: data.parsed_features, server: data.server, time: new Date().toLocaleString() }, ...prev])
      message.success(`上传成功，解析 ${data?.parsed_features ?? 0} 个 feature`)
    } finally {
      setUploading(false)
    }
  }

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Card>
        <Typography.Title level={4} style={{ marginTop: 0 }}>数据接入 / License 导入</Typography.Title>
        <Typography.Text type="secondary">
          将 license 文件导入系统，刷新 Feature 视图，并在测试环境中验证 Dashboard / License Keys / Alerts 的联动效果。
        </Typography.Text>
        <Divider />
        <Alert
          type="info"
          showIcon
          message="当前联调目标环境"
          description="192.168.110.128（模拟生产环境，已部署完整 license 与 license 服务）"
          style={{ marginBottom: 16 }}
        />
        <Dragger
          beforeUpload={() => false}
          maxCount={1}
          fileList={fileList}
          onChange={({ fileList: next }) => setFileList(next.slice(-1))}
          style={{ padding: 16 }}
        >
          <p className="ant-upload-drag-icon"><InboxOutlined /></p>
          <p className="ant-upload-text">点击或拖拽上传 .lic / .dat / .txt 文件</p>
          <p className="ant-upload-hint">建议优先使用测试环境中的真实 license 文件做联调验证</p>
        </Dragger>
        <Space style={{ marginTop: 16 }}>
          <Button type="primary" icon={<UploadOutlined />} onClick={onUpload} loading={uploading}>上传并解析</Button>
          <Button onClick={() => { setFileList([]); setResult(null) }}>清空</Button>
        </Space>
      </Card>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="解析结果预览" style={{ height: '100%' }}>
            {result ? (
              <Descriptions column={1} bordered size="small">
                <Descriptions.Item label="文件名">{result.filename}</Descriptions.Item>
                <Descriptions.Item label="识别服务">{result.server}</Descriptions.Item>
                <Descriptions.Item label="端口">{result.port}</Descriptions.Item>
                <Descriptions.Item label="解析到的 Feature 数">{result.parsed_features}</Descriptions.Item>
                <Descriptions.Item label="状态">{result.ok ? '成功' : '失败'}</Descriptions.Item>
              </Descriptions>
            ) : (
              <Typography.Text type="secondary">上传文件后，这里会显示解析结果预览。</Typography.Text>
            )}
          </Card>
        </Col>
        <Col span={12}>
          <Card title="联调检查建议" style={{ height: '100%' }}>
            <ul style={{ paddingLeft: 18, margin: 0 }}>
              <li>上传成功后，返回 Dashboard 检查统计卡片是否变化</li>
              <li>进入 Feature 使用情况页确认新增/更新的 feature</li>
              <li>进入 Alerts 页确认是否生成 license_upload 告警</li>
              <li>如使用真实日志，请再检查 Logs 页是否能检索到相关 vendor 日志</li>
            </ul>
          </Card>
        </Col>
      </Row>

      <Card title="本次会话导入历史">
        <Table
          rowKey="key"
          dataSource={history}
          pagination={{ pageSize: 5 }}
          columns={[
            { title: '文件名', dataIndex: 'filename' },
            { title: '服务', dataIndex: 'server' },
            { title: '解析数', dataIndex: 'parsed', width: 100 },
            { title: '时间', dataIndex: 'time', width: 180 },
          ]}
        />
      </Card>
    </Space>
  )
}
