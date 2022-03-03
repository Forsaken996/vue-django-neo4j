
//生产环境环境变量配置
const ServerName = `a`;//服务器a名称
// const ServerName = `b`;//服务器b名称

//切换服务器地址与本地地址
// const dataServer = `http://${ServerName}.ik.cn/api`;//服务器端服务地址
const dataServer = `http://49.233.255.82:8000/api/`;//本地服务地址

//变量导出
module.exports = {
  DataServer : dataServer,//服务器地址
  ImgServer : `http://${ServerName}/images/`,//图片服务地址
  AudioServer : `http://${ServerName}/audio/`,//音频服务地址
}
